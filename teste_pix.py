# test_pix.py
import os
from utils.pagamentos import criar_sandbox_test_user, criar_cobranca_mercadopago
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=== Criando Test User ===")
    email = criar_sandbox_test_user()
    if not email:
        print("❌ Falha ao criar test user")
        return
    print("✅ Test user criado:", email)

    print("\n=== Criando Cobrança Pix ===")
    dados = criar_cobranca_mercadopago(10.0)
    if not dados:
        print("❌ Falha ao criar cobrança Pix")
    else:
        print("✅ Cobrança criada ID:", dados["id"])
        print("QR Code (base64):", dados["qr_code_base64"][:60], "…")

if __name__ == "__main__":
    main()
