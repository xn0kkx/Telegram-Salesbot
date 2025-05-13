import os
import aiohttp
import logging
import base64
import uuid
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

EFI_CLIENT_ID = os.getenv("EFI_CLIENT_ID")
EFI_CLIENT_SECRET = os.getenv("EFI_CLIENT_SECRET")
EFI_PIX_KEY = os.getenv("EFI_PIX_KEY")
BASE_URL = "https://pix.api.efipay.com.br"

TOKEN_CACHE = {"access_token": None, "expires_in": 0}

async def obter_token_efi():
    """
    Autentica na API da Efi e retorna um token de acesso.
    """
    global TOKEN_CACHE
    url = f"{BASE_URL}/oauth/token"
    headers = {"Content-Type": "application/json"}
    payload = {
        "grant_type": "client_credentials"
    }
    auth = aiohttp.BasicAuth(EFI_CLIENT_ID, EFI_CLIENT_SECRET)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers, auth=auth) as resp:
                data = await resp.json()
                if resp.status == 200:
                    TOKEN_CACHE["access_token"] = data["access_token"]
                    return data["access_token"]
                else:
                    logger.error("Erro ao obter token [%s]: %s", resp.status, data)
        except Exception as e:
            logger.exception("Erro ao obter token Efi: %s", e)
    return None

async def criar_cobranca_efi(user_id: int, valor: float) -> dict | None:
    """
    Cria uma cobrança Pix na Efi.
    """
    token = await obter_token_efi()
    if not token:
        return None

    if not EFI_PIX_KEY:
        logger.error("Chave Pix da Efi não definida no .env (EFI_PIX_KEY)")
        return None

    try:
        valor_decimal = Decimal(str(valor)).quantize(Decimal("0.00"))
    except InvalidOperation:
        logger.error("Valor inválido: %s", valor)
        return None

    txid = str(uuid.uuid4()).replace("-", "")[:35]
    url = f"{BASE_URL}/v2/cob/{txid}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "calendario": {"expiracao": 3600},
        "devedor": {
            "cpf": "12345678909",
            "nome": f"Usuário {user_id}"
        },
        "valor": {"original": str(valor_decimal)},
        "chave": EFI_PIX_KEY,
        "infoAdicionais": [
            {"nome": "Plano", "valor": f"R$ {valor_decimal}"}
        ]
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.put(url, headers=headers, json=payload) as resp:
                cobranca = await resp.json()
                if resp.status in (200, 201) and "loc" in cobranca:
                    # Solicita o QR Code
                    qr_url = f"{BASE_URL}/v2/loc/{cobranca['loc']['id']}/qrcode"
                    async with session.get(qr_url, headers=headers) as qr_resp:
                        qr_data = await qr_resp.json()
                        return {
                            "id": txid,
                            "link": cobranca['loc'].get('location'),
                            "qr_code": qr_data.get("qrcode"),
                            "qr_code_base64": qr_data.get("imagemQrcode")
                        }
                else:
                    logger.error("Erro ao criar cobrança [%s]: %s", resp.status, cobranca)
        except Exception as e:
            logger.exception("Erro ao criar cobrança Efi: %s", e)
    return None

async def verificar_status_efi(payment_id: str) -> str | None:
    """
    Verifica o status da cobrança na Efi via TXID.
    """
    token = await obter_token_efi()
    if not token:
        return None

    url = f"{BASE_URL}/v2/cob/{payment_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if resp.status == 200:
                    status = data.get("status")
                    logger.info("Status da cobrança %s: %s", payment_id, status)
                    return status
                else:
                    logger.error("Erro ao verificar status [%s]: %s", resp.status, data)
        except Exception as e:
            logger.exception("Erro ao verificar status Efi: %s", e)
    return None