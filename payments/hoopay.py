import os
import logging
import aiohttp
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

CLIENT_ID = os.getenv("HOOPAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("HOOPAY_CLIENT_SECRET")
ORGANIZATION_ID = os.getenv("HOOPAY_ORGANIZATION")
BASE_URL = "https://api.pay.hoopay.com.br"

async def criar_cobranca_hoopay(user_id: int, valor: float) -> dict | None:
    """
    Cria uma cobrança via PIX na API da Hoopay.
    Inclui customer genérico e split para organização.
    """
    if not CLIENT_ID or not CLIENT_SECRET:
        logger.error("Credenciais da Hoopay não definidas no .env")
        return None

    try:
        valor_decimal = Decimal(str(valor)).quantize(Decimal("0.00"))
    except InvalidOperation:
        logger.error("Valor inválido: %s", valor)
        return None

    url = f"{BASE_URL}/charge"
    payload = {
        "amount": float(valor_decimal),
        "customer": {
            "email": f"{user_id}@anon.io",
            "name": f"Cliente {user_id}",
            "phone": "11999999999",
            "document": "00000000191"
        },
        "products": [
            {
                "title": "PIX",
                "amount": float(valor_decimal),
                "quantity": 1
            }
        ],
        "payments": [
            {
                "amount": float(valor_decimal),
                "type": "pix"
            }
        ],
        "split": [
            {
                "organization": ORGANIZATION_ID,
                "type": "percentage",
                "amount": 100
            }
        ],
        "data": {
            "ip": "192.168.0.1"
        }
    }

    auth = aiohttp.BasicAuth(CLIENT_ID, CLIENT_SECRET)

    async with aiohttp.ClientSession(auth=auth) as session:
        try:
            resp = await session.post(url, json=payload)
            data = await resp.json()

            if resp.status == 200 and "payment" in data:
                try:
                    charge = data["payment"]["charges"][0]
                    pix_payload = charge.get("pixPayload")
                    pix_qrcode = charge.get("pixQrCode")
                    payment_url = data.get("data", {}).get("url", "")

                    if pix_payload and pix_qrcode:
                        logger.info("Cobrança criada com UUID %s", charge.get("uuid"))
                        return {
                            "id": charge.get("uuid"),
                            "link": payment_url,
                            "qr_code": pix_payload,
                            "qr_code_base64": pix_qrcode
                        }
                    else:
                        logger.error("Cobrança criada mas faltam dados de PIX: %s", charge)
                except Exception as e:
                    logger.exception("Erro ao processar resposta da cobrança: %s", e)
            else:
                logger.error("Erro criação da cobrança [%s]: %s", resp.status, data)
        except Exception as e:
            logger.exception("Erro ao criar cobrança Hoopay: %s", e)
    return None

async def verificar_status_hoopay(payment_id: str) -> str | None:
    """
    Verifica o status da cobrança via UUID na API da Hoopay.
    """
    if not CLIENT_ID or not CLIENT_SECRET:
        logger.error("Credenciais da Hoopay não definidas no .env")
        return None

    url = f"{BASE_URL}/pix/consult/{payment_id}"
    auth = aiohttp.BasicAuth(CLIENT_ID, CLIENT_SECRET)

    async with aiohttp.ClientSession(auth=auth) as session:
        try:
            resp = await session.get(url)
            data = await resp.json()

            if resp.status == 200:
                if "payment" in data:
                    status = data["payment"].get("status")
                elif "result" in data:
                    status = data["result"].get("status")
                else:
                    logger.error("Resposta inesperada ao consultar status: %s", data)
                    return None

                logger.info("Status da cobrança %s: %s", payment_id, status)
                return status
            else:
                logger.error("Erro ao consultar status [%s]: %s", resp.status, data)
        except Exception as e:
            logger.exception("Erro ao verificar status Hoopay: %s", e)
    return None