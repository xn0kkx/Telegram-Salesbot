import asyncio
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

async def agendar_upsell(user_id: int, bot: Bot):
    await asyncio.sleep(300)  # 5 minutos
    await bot.send_message(user_id, "📢 Aproveite nossa oferta especial de upsell!")

async def agendar_remarketing(user_id: int, bot: Bot):
    delays = [1200, 86400, 259200]  # 20min, 1dia, 3dias
    for delay in delays:
        await asyncio.sleep(delay)
        await bot.send_message(user_id, "⏳ Lembrete: finalize seu pagamento via Pix!")
