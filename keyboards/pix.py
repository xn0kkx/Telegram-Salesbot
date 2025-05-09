from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton

def copiar_pix_keyboard(pix_code: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📋 Copiar Código PIX",
                    copy_text=CopyTextButton(text=pix_code)
                )
            ]
        ]
    )
