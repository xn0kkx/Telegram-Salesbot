from aiogram.utils.keyboard import InlineKeyboardBuilder

REMARKETING_PLANOS = [
    {"texto": "📦 Reativar Plano Básico - R$ 10", "valor": 10},
    {"texto": "🎯 Reativar Premium - R$ 25", "valor": 25},
    {"texto": "🚀 Reativar VIP - R$ 50", "valor": 50}
]

def remarketing_keyboard():
    builder = InlineKeyboardBuilder()
    for plano in REMARKETING_PLANOS:
        builder.button(text=plano["texto"], callback_data=f"remarketing:{plano['valor']}")
    builder.adjust(1)
    return builder.as_markup()
