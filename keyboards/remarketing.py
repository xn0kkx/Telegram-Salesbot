import os
from dotenv import load_dotenv
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

REMARKETING_PLANOS = [
    {
        "texto": os.getenv("REMARKETING_BASICO_TEXTO"),
        "valor": float(os.getenv("REMARKETING_BASICO_VALOR"))
    },
    {
        "texto": os.getenv("REMARKETING_PREMIUM_TEXTO"),
        "valor": float(os.getenv("REMARKETING_PREMIUM_VALOR"))
    },
    {
        "texto": os.getenv("REMARKETING_VIP_TEXTO"),
        "valor": float(os.getenv("REMARKETING_VIP_VALOR"))
    }
]

def remarketing_keyboard():
    builder = InlineKeyboardBuilder()
    for plano in REMARKETING_PLANOS:
        builder.button(text=plano["texto"], callback_data=f"remarketing:{plano['valor']}")
    builder.adjust(1)
    return builder.as_markup()
