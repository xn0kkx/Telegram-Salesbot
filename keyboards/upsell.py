import os
from dotenv import load_dotenv
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

UPSELL_PLANOS = [
    {
        "texto": os.getenv("UPSELL_PREMIUM_TEXTO"),
        "valor": float(os.getenv("UPSELL_PREMIUM_VALOR"))
    },
    {
        "texto": os.getenv("UPSELL_VIP_TEXTO"),
        "valor": float(os.getenv("UPSELL_VIP_VALOR"))
    }
]

def upsell_keyboard(plano_valor: float | None):
    planos = [p for p in UPSELL_PLANOS if p["valor"] > (plano_valor or 0)]
    builder = InlineKeyboardBuilder()
    for plano in planos:
        builder.button(text=plano["texto"], callback_data=f"upsell:{plano['valor']}")
    builder.adjust(1)
    return builder.as_markup()
