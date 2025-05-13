import os
import uuid
import logging
import aiohttp
from decimal import Decimal, InvalidOperation
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
BASE_URL = "https://api.mercadopago.com"

async def criar_cobranca_mercadopago(user_id: int, valor: float) -> dict | None:
    """
    Cria uma cobrança Pix no MercadoPago sem pedir dados ao usuário.
    Usa e-mail fake f'{user_id}@example.com' apenas para satisfazer o requisito da API.
    Retorna dict com: id, link (ticket_url), qr_code e qr_code_base64.
    """
    if not MP_ACCESS_TOKEN:
        logger.error("MP_ACCESS_TOKEN não encontrado no .env")
        return None

    # Formata valor com duas casas decimais
    try:
        valor_decimal = Decimal(str(valor)).quantize(Decimal("0.00"))
    except InvalidOperation:
        logger.error("Valor inválido para cobrança: %s", valor)
        return None

    url = f"{BASE_URL}/v1/payments"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}",
        "x-idempotency-key": str(uuid.uuid4())
    }
    payload = {
        "transaction_amount": float(valor_decimal),
        "payment_method_id": "pix",
        "description": f"Pagamento via Pix - R$ {valor_decimal}",
        "payer": {"email": f"{user_id}@example.com"}
    }

    async with aiohttp.ClientSession() as session:
        try:
            resp = await session.post(url, json=payload, headers=headers)
            data = await resp.json()
            if resp.status in (200, 201):
                txn = data.get("point_of_interaction", {}) \
                          .get("transaction_data", {})
                logger.info("Cobrança criada com ID %s", data.get("id"))
                return {
                    "id": data.get("id"),
                    "link": txn.get("ticket_url"),
                    "qr_code": txn.get("qr_code"),
                    "qr_code_base64": txn.get("qr_code_base64")
                }
            else:
                logger.error("Erro criação da cobrança [%s]: %s", resp.status, data)
        except Exception as e:
            logger.exception("Exceção ao criar cobrança: %s", e)
    return None

async def verificar_status_mercadopago(payment_id: str) -> str | None:
    """
    Consulta status de uma cobrança Pix pelo ID.
    Retorna 'approved', 'pending', etc., ou None em caso de erro.
    """
    if not MP_ACCESS_TOKEN:
        logger.error("MP_ACCESS_TOKEN não encontrado no .env")
        return None

    url = f"{BASE_URL}/v1/payments/{payment_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MP_ACCESS_TOKEN}"
    }

    async with aiohttp.ClientSession() as session:
        try:
            resp = await session.get(url, headers=headers)
            data = await resp.json()
            if resp.status == 200:
                status = data.get("status")
                logger.info("Status da cobrança %s: %s", payment_id, status)
                return status
            else:
                logger.error("Erro ao consultar status [%s]: %s", resp.status, data)
        except Exception as e:
            logger.exception("Exceção ao verificar status: %s", e)
    return None
