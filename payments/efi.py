import os
import uuid
import logging
import aiohttp
import ssl
import time
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

ENV = os.getenv("ENV", "prod").lower()
CLIENT_ID = os.getenv("EFI_CLIENT_ID")
CLIENT_SECRET = os.getenv("EFI_CLIENT_SECRET")
PIX_KEY = os.getenv("EFI_PIX_KEY")
CERT_PEM_PATH = os.getenv("EFI_CERT_PEM")
KEY_PEM_PATH = os.getenv("EFI_KEY_PEM")

if ENV == "prod":
    AUTH_URL = "https://pix.api.efipay.com.br"
    BASE_URL = "https://pix.api.efipay.com.br"
else:
    AUTH_URL = "https://pix-h.api.efipay.com.br"
    BASE_URL = "https://pix-h.api.efipay.com.br"

# Cache de token
_token_cache = {
    "access_token": None,
    "expires_at": 0
}

def get_ssl_context():
    try:
        context = ssl.create_default_context()
        context.load_cert_chain(certfile=CERT_PEM_PATH, keyfile=KEY_PEM_PATH)
        logger.debug("✅ Certificados carregados com sucesso.")
        return context
    except Exception as e:
        logger.exception("❌ Erro ao carregar certificados PEM: %s", e)
        return None

async def obter_token() -> str | None:
    now = time.time()
    if _token_cache["access_token"] and _token_cache["expires_at"] > now:
        logger.debug("🔄 Token da Efí reutilizado do cache.")
        return _token_cache["access_token"]

    logger.debug("🔐 Solicitando novo token de autenticação à Efí...")
    url = f"{AUTH_URL}/oauth/token"
    headers = {"Content-Type": "application/json"}
    auth = aiohttp.BasicAuth(CLIENT_ID, CLIENT_SECRET)
    payload = {
        "grant_type": "client_credentials",
        "scope": "cob.read cob.write pix.read pix.write webhook.read webhook.write"
    }

    ssl_context = get_ssl_context()
    if not ssl_context:
        return None

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, headers=headers, auth=auth, json=payload, ssl=ssl_context) as resp:
                data = await resp.json()
                logger.debug("🔁 Resposta token: %s", data)
                if resp.status == 200:
                    token = data.get("access_token")
                    expires_in = int(data.get("expires_in", 3600))
                    _token_cache["access_token"] = token
                    _token_cache["expires_at"] = now + expires_in - 60
                    logger.info("✅ Token obtido e armazenado no cache.")
                    return token
                logger.error("❌ Erro ao obter token [%s]: %s", resp.status, data)
        except Exception as e:
            logger.exception("❌ Exceção ao obter token: %s", e)
    return None

async def inicializar_efi():
    if await obter_token():
        logger.info("🚀 Token da Efí inicializado com sucesso.")
    else:
        logger.warning("⚠ Não foi possível inicializar o token da Efí.")

async def criar_cobranca_efi(user_id: int, valor: float) -> dict | None:
    try:
        valor_decimal = Decimal(str(valor)).quantize(Decimal("0.00"))
        logger.debug("💰 Valor formatado: R$ %.2f", valor_decimal)
    except InvalidOperation:
        logger.error("❌ Valor inválido: %s", valor)
        return None

    token = await obter_token()
    if not token:
        return None

    txid = uuid.uuid4().hex[:26]
    url = f"{BASE_URL}/v2/cob/{txid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "calendario": {"expiracao": 3600},
        "devedor": {
            "cpf": "12345678909",
            "nome": f"User {user_id}"
        },
        "valor": {"original": f"{valor_decimal:.2f}"},
        "chave": PIX_KEY,
        "solicitacaoPagador": "Pagamento via Pix"
    }

    logger.debug("📦 Enviando payload de cobrança: %s", payload)
    ssl_context = get_ssl_context()
    if not ssl_context:
        return None

    async with aiohttp.ClientSession() as session:
        try:
            async with session.put(url, headers=headers, json=payload, ssl=ssl_context) as resp:
                data = await resp.json()
                logger.debug("📥 Resposta da criação da cobrança: %s", data)
                if resp.status in (200, 201):
                    loc_id = data.get("loc", {}).get("id")
                    if loc_id:
                        return await obter_qrcode(token, loc_id, txid)
                logger.error("❌ Erro na criação da cobrança [%s]: %s", resp.status, data)
        except Exception as e:
            logger.exception("❌ Exceção ao criar cobrança: %s", e)
    return None

async def obter_qrcode(token: str, loc_id: int, txid: str) -> dict | None:
    logger.debug("🔍 Solicitando QR Code da cobrança loc_id=%s", loc_id)
    url = f"{BASE_URL}/v2/loc/{loc_id}/qrcode"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    ssl_context = get_ssl_context()
    if not ssl_context:
        return None

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, ssl=ssl_context) as resp:
                data = await resp.json()
                logger.debug("📥 Resposta do QR Code: %s", data)
                if resp.status == 200:
                    return {
                        "id": txid,
                        "link": None,
                        "qr_code": data.get("qrcode"),
                        "qr_code_base64": data.get("imagemQrcode")
                    }
                logger.error("❌ Erro ao obter QR Code [%s]: %s", resp.status, data)
        except Exception as e:
            logger.exception("❌ Exceção ao obter QR Code: %s", e)
    return None

async def verificar_status_efi(txid: str) -> str | None:
    logger.debug("🔎 Verificando status da cobrança: %s", txid)
    token = await obter_token()
    if not token:
        return None

    url = f"{BASE_URL}/v2/cob/{txid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    ssl_context = get_ssl_context()
    if not ssl_context:
        return None

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, ssl=ssl_context) as resp:
                data = await resp.json()
                logger.debug("📥 Resposta status cobrança: %s", data)
                if resp.status == 200:
                    status = data.get("status")
                    logger.info("📊 Status da cobrança %s: %s", txid, status)
                    return status
                logger.error("❌ Erro ao consultar status [%s]: %s", resp.status, data)
        except Exception as e:
            logger.exception("❌ Exceção ao verificar status: %s", e)
    return None