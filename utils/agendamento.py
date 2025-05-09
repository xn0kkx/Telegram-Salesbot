import asyncio
from aiogram import Bot

async def agendar_upsell(user_id: int, bot: Bot):
    await asyncio.sleep(300)  # 5 minutos
    await bot.send_message(user_id, "📢 Oferta especial de upsell!")

async def agendar_remarketing(user_id: int, bot: Bot):
    delays = [120, 300, 600]  # 2min, 5min, 10min
    mensagens = [
        "🔔 Ainda dá tempo de aproveitar nossa oferta! ⏰",
        "💡 Temos algo especial reservado pra você!",
        "📣 Última chance: finalize seu pagamento e garanta bônus exclusivos!"
    ]
    for delay, msg in zip(delays, mensagens):
        await asyncio.sleep(delay)
        await bot.send_message(user_id, msg)
