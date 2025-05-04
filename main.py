import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from dotenv import load_dotenv
from database import db
from keyboards import planos
from utils import pagamentos, agendamento

# Configuração inicial
load_dotenv()
db.init_db()

BOT_TOKENS = os.getenv("BOT_TOKENS", "").split(",")
BOT_TOKENS = [token.strip() for token in BOT_TOKENS if token.strip()]

bots = [Bot(token=token) for token in BOT_TOKENS]
dispatchers = [Dispatcher() for _ in BOT_TOKENS]

# Handlers
async def start(message: types.Message):
    db.add_user(message.from_user.id)
    await message.answer_photo(
        photo="",
        caption="🛍️ Bem-vindo! Escolha seu plano:",
        reply_markup=planos.planos_keyboard()
    )

async def handle_plano(callback: types.CallbackQuery):
    valor = callback.data.split(":")[1]
    cobranca = pagamentos.criar_cobranca_efi(float(valor))
    await callback.message.answer_photo(
        photo=cobranca["imagem_qrcode"],
        caption=f"💵 PIX: {cobranca['codigo_pix']}"
    )

async def verificar_pagamento(callback: types.CallbackQuery):
    payment_id, status = db.get_payment(callback.from_user.id)
    if status == "approved":
        await callback.message.answer("✅ Pagamento confirmado!")
    else:
        await callback.message.answer("❌ Pagamento pendente!")

# Registra handlers
for dp in dispatchers:
    dp.message.register(start, Command("start"))
    dp.callback_query.register(handle_plano, F.data.startswith("plano:"))
    dp.callback_query.register(verificar_pagamento, F.data == "verificar_pagamento")

# Inicia bots
async def main():
    await asyncio.gather(*[
        dp.start_polling(bot) for dp, bot in zip(dispatchers, bots)
    ])

if __name__ == "__main__":
    asyncio.run(main())