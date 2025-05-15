from aiogram.utils.keyboard import InlineKeyboardBuilder

REMARKETING_PLANOS = [
    {"texto": "📦 Reativar Plano Básico - R$ 10", "valor": 1},
    {"texto": "🎯 Reativar Premium - R$ 25", "valor": 2},
    {"texto": "🚀 Reativar VIP - R$ 50", "valor": 3}
]

def remarketing_keyboard():
    builder = InlineKeyboardBuilder()
    for plano in REMARKETING_PLANOS:
        builder.button(text=plano["texto"], callback_data=f"remarketing:{plano['valor']}")
    builder.adjust(1)
    return builder.as_markup()
