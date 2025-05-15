import asyncio
from aiogram import Bot
from database import db
from keyboards.upsell import upsell_keyboard
from keyboards.remarketing import remarketing_keyboard

async def agendar_upsell(user_id: int, bot: Bot):
    await asyncio.sleep(30)
    plano_valor = db.get_plano(user_id)
    teclado = upsell_keyboard(plano_valor)
    if teclado.inline_keyboard:
        await bot.send_message(
            chat_id=user_id,
            text="🎁 Oferta Especial!\n\nAproveite esta oferta exclusiva disponível por tempo limitado.",
            reply_markup=teclado
        )

async def agendar_remarketing(user_id: int, bot: Bot):
    delays = [120, 300, 600]
    mensagens = [
        "🔔 Ainda dá tempo de aproveitar nossa oferta! ⏰",
        "💡 Temos algo especial reservado pra você!",
        "📣 Última chance: finalize seu pagamento e garanta bônus exclusivos!"
    ]
    for delay, msg in zip(delays, mensagens):
        await asyncio.sleep(delay)
        await bot.send_message(
            chat_id=user_id,
            text=msg,
            reply_markup=remarketing_keyboard()
        )