import asyncio
from aiogram import Bot
from database import db
from keyboards.planos import planos_keyboard_excluindo

async def agendar_upsell(user_id: int, bot: Bot):
    await asyncio.sleep(300)
    plano_valor = db.get_plano(user_id)
    teclado = planos_keyboard_excluindo(plano_valor, incluir_verificar=False)

    if teclado.inline_keyboard:  # só envia se houver planos superiores
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
    plano_valor = db.get_plano(user_id)
    for delay, msg in zip(delays, mensagens):
        await asyncio.sleep(delay)
        await bot.send_message(
            chat_id=user_id,
            text=msg + "\n\n👇 Escolha um plano para continuar:",
            reply_markup=planos_keyboard_excluindo(plano_valor)
        )
