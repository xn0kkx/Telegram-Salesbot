import os
from dotenv import load_dotenv
from aiogram.utils.keyboard import InlineKeyboardBuilder

load_dotenv()

def get_dynamic_planos(prefix: str):
    planos = []
    i = 1
    while True:
        texto_key = f"{prefix}_{i}_TEXTO"
        valor_key = f"{prefix}_{i}_VALOR"
        texto = os.getenv(texto_key)
        valor = os.getenv(valor_key)
        if texto is None or valor is None:
            break
        try:
            planos.append({
                "texto": texto,
                "valor": float(valor)
            })
        except ValueError:
            continue
        i += 1
    return planos

REMARKETINGS = get_dynamic_planos("REMARKETING")

def remarketing_keyboard():
    return _build_keyboard(REMARKETINGS)

def remarketing_keyboard_excluindo(plano_valor: float | None):
    if plano_valor is None:
        planos_filtrados = REMARKETINGS
    else:
        planos_filtrados = [p for p in REMARKETINGS if p["valor"] > plano_valor]
    return _build_keyboard(planos_filtrados)

def _build_keyboard(planos: list[dict]):
    builder = InlineKeyboardBuilder()
    for plano in planos:
        builder.button(text=plano["texto"], callback_data=f"remarketing:{plano['valor']}")
    builder.adjust(1)
    return builder.as_markup()
