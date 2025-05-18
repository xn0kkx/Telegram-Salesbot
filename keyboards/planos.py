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
    return _build_keyboard(PLANOS)

def planos_keyboard_excluindo(plano_valor: float | None):
    if plano_valor is None:
        planos_filtrados = PLANOS
    else:
        planos_filtrados = [p for p in PLANOS if p["valor"] > plano_valor]
    return _build_keyboard(planos_filtrados)

def _build_keyboard(planos: list[dict]):
    builder = InlineKeyboardBuilder()
    for plano in planos:
        builder.button(text=plano["texto"], callback_data=f"plano:{plano['valor']}")
    builder.adjust(1)
    return builder.as_markup()