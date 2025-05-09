import os
import asyncio
import base64
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv
from database import db
from keyboards import planos
from keyboards.pix import copiar_pix_keyboard
from utils import pagamentos, agendamento

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('bot.log')]
)

load_dotenv()
ENV = os.getenv("ENV", "prod")
db.init_db()

BOT_TOKENS = [t.strip() for t in os.getenv("BOT_TOKENS", "").split(",") if t.strip()]
bots = [Bot(token=token) for token in BOT_TOKENS]
dispatchers = [Dispatcher() for _ in BOT_TOKENS]

PIX_CODES = {}

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
        db.update_payment(callback.from_user.id, cobranca["id"], "pending")

        await callback.message.answer(
            f"🔗 *Link de Pagamento*: [Clique aqui]({cobranca['link']})\n\n"
            "💱 Ou escaneie o QR Code abaixo para pagar via PIX:",
            parse_mode="Markdown"
        )

        qr_image = criar_qrcode_temp(cobranca["qr_code_base64"])
        if qr_image:
            await callback.message.answer_photo(photo=qr_image)
        else:
            await callback.message.answer("❌ Erro ao gerar imagem do QR Code!")

        pix_code = cobranca.get("qr_code", "")
        if pix_code:
            PIX_CODES[callback.from_user.id] = pix_code
            await callback.message.answer(
                "📋 *Clique abaixo para copiar o código PIX:*",
                reply_markup=copiar_pix_keyboard(pix_code),
                parse_mode="Markdown"
            )

        # Simulações de ambiente
        if ENV == "dev":
            asyncio.create_task(simular_pagamento_aprovado(callback.from_user.id, callback.bot, cobranca["id"]))
        elif ENV == "dev_recusado":
            asyncio.create_task(simular_pagamento_recusado(callback.from_user.id, callback.bot, cobranca["id"]))

    else:
        logging.error("Falha na geração da cobrança")
        await callback.message.answer("⚠️ Erro ao gerar cobrança!")

async def copiar_pix(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    pix_code = PIX_CODES.get(user_id)
    if pix_code:
        await callback.message.answer(
            f"🔢 Código PIX:\n<code>{pix_code}</code>",
            parse_mode="HTML"
        )
    else:
        await callback.message.answer("❌ Código PIX não encontrado.")

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
        await callback.message.edit_reply_markup()
        await callback.message.answer("✅ Pagamento confirmado! Aqui está seu link: https://seusite.com/produto")
        asyncio.create_task(agendamento.agendar_upsell(callback.from_user.id, callback.bot))
    else:
        await callback.message.answer("❌ Pagamento ainda não confirmado.")

async def agendar_upsell(user_id: int, bot: Bot):
    await asyncio.sleep(300)
    texto_upsell = (
        "🎁 Oferta Especial!\n\n"
        "Aproveite esta oferta exclusiva disponível por tempo limitado. "
        "Clique no botão abaixo para saber mais."
    )
    botao_upsell = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔓 Acessar Oferta", url="https://seusite.com/upsell")]
    ])
    await bot.send_message(chat_id=user_id, text=texto_upsell, reply_markup=botao_upsell)

async def simular_pagamento_aprovado(user_id: int, bot: Bot, payment_id: str):
    await asyncio.sleep(60)
    db.update_payment(user_id, payment_id, "approved")
    await bot.send_message(user_id, "✅ Pagamento confirmado automaticamente (simulação). Aqui está seu link: https://seusite.com/produto")
    await agendar_upsell(user_id, bot)

async def simular_pagamento_recusado(user_id: int, bot: Bot, payment_id: str):
    await asyncio.sleep(300)
    # Checa se ainda está pending
    atual = db.get_payment(user_id)
    if atual and atual[1] != "approved":
        db.update_payment(user_id, payment_id, "rejected")
        await bot.send_message(user_id, "❌ Pagamento recusado automaticamente (simulação).")
        asyncio.create_task(agendamento.agendar_remarketing(user_id, bot))

# Registros
for dp in dispatchers:
    dp.message.register(start, Command("start"))
    dp.message.register(reset_conversation, Command("reset"))
    dp.callback_query.register(handle_plano, F.data.startswith("plano:"))
    dp.callback_query.register(verificar_pagamento, F.data == "verificar_pagamento")
    dp.callback_query.register(copiar_pix, F.data == "copiar_pix")

async def main():
    await asyncio.gather(*[dp.start_polling(bot) for dp, bot in zip(dispatchers, bots)])

if __name__ == "__main__":
    asyncio.run(main())