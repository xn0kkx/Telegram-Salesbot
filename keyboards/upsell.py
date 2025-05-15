from aiogram.utils.keyboard import InlineKeyboardBuilder

UPSELL_PLANOS = [
    {"texto": "🎯 Upgrade para Premium - R$ 2", "valor": 1},
    {"texto": "🚀 Upgrade para VIP - R$ 3", "valor": 2}
]

def upsell_keyboard(plano_valor: float | None):
    planos = [p for p in UPSELL_PLANOS if p["valor"] > (plano_valor or 0)]
    builder = InlineKeyboardBuilder()
    for plano in planos:
        builder.button(text=plano["texto"], callback_data=f"upsell:{plano['valor']}")
    builder.adjust(1)
    return builder.as_markup()
