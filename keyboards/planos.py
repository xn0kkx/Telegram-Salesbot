import os
from dotenv import load_dotenv
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

PLANOS = [
    {
        "texto": os.getenv("PLANO_BASICO_TEXTO"),
        "valor": float(os.getenv("PLANO_BASICO_VALOR"))
    },
    {
        "texto": os.getenv("PLANO_PREMIUM_TEXTO"),
        "valor": float(os.getenv("PLANO_PREMIUM_VALOR"))
    },
    {
        "texto": os.getenv("PLANO_VIP_TEXTO"),
        "valor": float(os.getenv("PLANO_VIP_VALOR"))
    }
]

def planos_keyboard():
    return _build_keyboard(PLANOS, incluir_verificar=True)

def planos_keyboard_excluindo(plano_valor: float | None, incluir_verificar: bool = True):
    if plano_valor is None:
        planos_filtrados = PLANOS
    else:
        planos_filtrados = [p for p in PLANOS if p["valor"] > plano_valor]
    return _build_keyboard(planos_filtrados, incluir_verificar)

def _build_keyboard(planos: list[dict], incluir_verificar: bool = True):
    builder = InlineKeyboardBuilder()
    for plano in planos:
        builder.button(text=plano["texto"], callback_data=f"plano:{plano['valor']}")
    if incluir_verificar and planos:
        builder.button(text="🔍 Verificar Pagamento", callback_data="verificar_pagamento")
    builder.adjust(1)
    return builder.as_markup()
