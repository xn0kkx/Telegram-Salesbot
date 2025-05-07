import os
import asyncio
import base64
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from database import db
from keyboards import planos
from utils import pagamentos, agendamento

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('bot.log')]
)

load_dotenv()
db.init_db()

BOT_TOKENS = [t.strip() for t in os.getenv("BOT_TOKENS", "").split(",") if t.strip()]
bots = [Bot(token=token) for token in BOT_TOKENS]
dispatchers = [Dispatcher() for _ in BOT_TOKENS]

def criar_qrcode_temp(base64_str: str):
    try:
        qr_data = base64.b64decode(base64_str)
        return BufferedInputFile(qr_data, filename="qrcode.png")
    except Exception as e:
        logging.error(f"Erro ao decodificar QR Code: {e}")
        return None

async def reset_conversation(message: types.Message, state: FSMContext):
    await state.clear()
    db.delete_user(message.from_user.id)
    await message.answer("♻️ Conversa reiniciada! Use /start para começar.")

async def start(message: types.Message):
    db.add_user(message.from_user.id)
    await message.answer_photo(
        photo="https://media-cdn.tripadvisor.com/media/attractions-splice-spp-720x480/12/28/df/5a.jpg",
        caption="🛍️ Bem-vindo! Escolha seu plano:",
        reply_markup=planos.planos_keyboard()
    )

async def handle_plano(callback: types.CallbackQuery):
    logging.info("Pedido de plano por %s", callback.from_user.id)
    valor = float(callback.data.split(":")[1])
    cobranca = await pagamentos.criar_cobranca_mercadopago(callback.from_user.id, valor)

    if cobranca and cobranca.get("link") and cobranca.get("qr_code_base64"):
        # 1) Salva no banco
        db.update_payment(callback.from_user.id, cobranca["id"], "pending")

        # 2) Envia o link de pagamento
        await callback.message.answer(
            f"🔗 *Link de Pagamento*: [Clique aqui]({cobranca['link']})\n\n"
            "💱 Ou escaneie o QR Code abaixo para pagar via PIX:",
            parse_mode="Markdown"
        )

        # 3) Envia a imagem do QR Code
        qr_image = criar_qrcode_temp(cobranca["qr_code_base64"])
        if qr_image:
            await callback.message.answer_photo(photo=qr_image)
        else:
            await callback.message.answer("❌ Erro ao gerar imagem do QR Code!")

        # 4) Envia o código PIX em bloco de código para cópia rápida
        pix_code = cobranca.get("qr_code", "")
        if pix_code:
            await callback.message.answer(
                "📋 *Código PIX (copie abaixo):*\n"
                f"```\n{pix_code}\n```",
                parse_mode="Markdown"
            )
    else:
        logging.error("Falha na geração da cobrança")
        await callback.message.answer("⚠️ Erro ao gerar cobrança!")

async def verificar_pagamento(callback: types.CallbackQuery):
    payment_data = db.get_payment(callback.from_user.id)
    if not payment_data:
        return await callback.message.answer("❌ Nenhum pagamento encontrado!")

    payment_id, _ = payment_data
    novo_status = await pagamentos.verificar_status_mercadopago(payment_id)

    if novo_status is None:
        logging.error("Não foi possível verificar status para %s", payment_id)
        await callback.message.answer("⚠️ Não foi possível verificar o pagamento no momento.")
        return

    if novo_status == "approved":
        db.update_payment(callback.from_user.id, payment_id, novo_status)
        await callback.message.edit_reply_markup()  # remove inline keyboard
        await callback.message.answer("✅ Pagamento confirmado! Aqui está seu link: [LINK_DO_PRODUTO]")
        asyncio.create_task(agendamento.agendar_upsell(callback.from_user.id, callback.bot))
    else:
        await callback.message.answer("❌ Pagamento ainda não confirmado.")

# Registra os handlers
for dp in dispatchers:
    dp.message.register(start, Command("start"))
    dp.message.register(reset_conversation, Command("reset"))
    dp.callback_query.register(handle_plano, F.data.startswith("plano:"))
    dp.callback_query.register(verificar_pagamento, F.data == "verificar_pagamento")

async def main():
    await asyncio.gather(*[dp.start_polling(bot) for dp, bot in zip(dispatchers, bots)])

if __name__ == "__main__":
    asyncio.run(main())
