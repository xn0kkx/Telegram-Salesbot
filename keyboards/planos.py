from aiogram.utils.keyboard import InlineKeyboardBuilder

def planos_keyboard():
    builder = InlineKeyboardBuilder()
    planos = [
        {"texto": "Plano Básico - R$ 10",   "valor": 10},
        {"texto": "Plano Premium - R$ 25",  "valor": 25},
        {"texto": "Plano VIP - R$ 50",      "valor": 50}
    ]
    for plano in planos:
        builder.button(text=plano["texto"], callback_data=f"plano:{plano['valor']}")
    builder.button(text="🔍 Verificar Pagamento", callback_data="verificar_pagamento")
    builder.adjust(1)
    return builder.as_markup()
