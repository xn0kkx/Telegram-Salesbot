import asyncio
import os
import logging
import httpx
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("efi_cert_test")

load_dotenv()

BASE_URL = "https://pix-h.api.efipay.com.br"
CLIENT_ID = os.getenv("EFI_CLIENT_ID")
CLIENT_SECRET = os.getenv("EFI_CLIENT_SECRET")

CERTS_PEM = {
    "Homologação": {
        "cert": os.getenv("EFI_CERT_PEM"),
        "key": os.getenv("EFI_KEY_PEM")
    }
    # Adicione produção aqui se necessário
}

async def obter_token(nome: str, cert_path: str, key_path: str):
    logger.info(f"🔍 Testando certificado: {nome}")

    if not all([CLIENT_ID, CLIENT_SECRET]):
        logger.error(f"❌ {nome}: Faltam EFI_CLIENT_ID ou EFI_CLIENT_SECRET no .env")
        return

    try:
        headers = {"Content-Type": "application/json"}
        payload = {
            "grant_type": "client_credentials",
            "scope": "cob.read cob.write pix.read pix.write webhook.read webhook.write"
        }

        async with httpx.AsyncClient(cert=(cert_path, key_path), verify=True, timeout=10) as client:
            resp = await client.post(
                f"{BASE_URL}/oauth/token",
                auth=(CLIENT_ID, CLIENT_SECRET),
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()
            token = resp.json().get("access_token")
            if token:
                logger.info(f"✅ {nome}: Token obtido com sucesso: {token[:40]}...")
            else:
                logger.warning(f"⚠️ {nome}: Resposta sem token.")
    except httpx.HTTPError as e:
        logger.error(f"❌ {nome}: Falha na requisição - {e}")
    except Exception as e:
        logger.exception(f"❌ {nome}: Erro inesperado")

async def main():
    tasks = []
    for nome, paths in CERTS_PEM.items():
        tasks.append(obter_token(nome, paths["cert"], paths["key"]))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
