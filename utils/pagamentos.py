import os
import mercadopago
import requests
from dotenv import load_dotenv

load_dotenv()

# Efí Bank (PIX)
def criar_cobranca_efi(valor: float):
    auth = {
        "client_id": os.getenv("EFI_CLIENT_ID"),
        "client_secret": os.getenv("EFI_CLIENT_SECRET")
    }
    
    token_response = requests.post(
        "https://api-pix.gerencianet.com.br/oauth/token",
        auth=(auth["client_id"], auth["client_secret"]),
        data={"grant_type": "client_credentials"}
    )
    
    access_token = token_response.json()["access_token"]
    
    response = requests.post(
        "https://api-pix.gerencianet.com.br/v2/cob",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"valor": valor}
    )
    
    return response.json()

# MercadoPago
def criar_cobranca_mercadopago(valor: float):
    sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_CLIENT_SECRET"))
    payment_data = {
        "transaction_amount": valor,
        "payment_method_id": "pix"
    }
    payment = sdk.payment().create(payment_data)
    return payment["response"]
