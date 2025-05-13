import os
import base64
import logging
import aiohttp
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

CLIENT_ID = os.getenv("HOOPAY_CLIENT_ID")
CLIENT_SECRET = os.getenv("HOOPAY_CLIENT_SECRET")
BASE_URL = "https://api.hoopay.com.br"

async def criar_cobranca_hoopay(user_id: int, valor: float) -> dict | None:
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    basic_auth_token = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {basic_auth_token}"
    }

    payload = {
        "amount": valor,
        "customer": {
            "email": f"{user_id}@example.com",
            "name": f"Usuário {user_id}",
            "phone": "11999999999",
            "document": "00000000000"
        },
        "products": [
            {
                "title": f"Plano de R$ {valor:.2f}",
                "amount": valor,
                "quantity": 1
            }
        ],
        "payments": [
            {
                "type": "pix",
                "amount": valor
            }
        ],
        "data": {
            "ip": "127.0.0.1"
        }
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/charge", json=payload, headers=headers) as response:
                data = await response.json()
                if response.status == 200 and data.get("payment", {}).get("status") == "pending":
                    charge = data["payment"]["charges"][0]
                    return {
                        "id": charge.get("uuid"),
                        "link": data.get("data", {}).get("url", ""),
                        "qr_code": charge.get("pixPayload"),
                        "qr_code_base64": charge.get("pixQrCode")
                    }
                else:
                    logger.error(f"Erro ao criar cobrança Hoopay: {data}")
    except Exception as e:
        logger.exception(f"Exceção na chamada da API Hoopay: {e}")
    
    return None

async def verificar_status_hoopay(order_uuid: str) -> str | None:
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    basic_auth_token = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {basic_auth_token}"
    }

    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}/pix/consult/{order_uuid}"
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                if resp.status == 200:
                    return data.get("payment", {}).get("status")
                else:
                    logger.error(f"Erro consultando status Hoopay: {data}")
    except Exception as e:
        logger.exception(f"Exceção ao consultar status Hoopay: {e}")

    return None