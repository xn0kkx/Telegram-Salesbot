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
from keyboards.pix import copiar_pix_keyboard
from utils import agendamento
from payments import hoopay, mercadopago, efi

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('bot.log')]
)

load_dotenv()
ENV = os.getenv("ENV", "prod")
PAYMENT_PROVIDER = os.getenv("PAYMENT_PROVIDER", "mercadopago").lower()
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
db.init_db()

BOT_TOKENS = [t.strip() for t in os.getenv("BOT_TOKENS", "").split(",") if t.strip()]
bots = [Bot(token=token) for token in BOT_TOKENS]
dispatchers = [Dispatcher() for _ in BOT_TOKENS]

PIX_CODES = {}

MENSAGENS_DIR = "mensagens"

def carregar_mensagem(nome_arquivo):
    caminho = os.path.join(MENSAGENS_DIR, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

def criar_qrcode_temp(base64_str: str):
    try:
        if base64_str.startswith("data:image"):
            base64_str = base64_str.split(",", 1)[1]
        qr_data = base64.b64decode(base64_str)
        return BufferedInputFile(qr_data, filename="qrcode.png")
    except Exception as e:
        logging.error(f"Erro ao decodificar QR Code: {e}")
        return None

def normalizar_status(status: str) -> str:
    status = status.lower()
    if status in ("paid", "approved", "concluida"):
        return "paid"
    elif status in ("pending", "waiting_payment", "aguardando"):
        return "pending"
    elif status in ("rejected", "cancelled", "cancelado", "falha"):
        return "rejected"
    return "unknown"

async def reset_conversation(message: types.Message, state: FSMContext):
    await state.clear()
    db.delete_user(message.from_user.id)
    await message.answer(carregar_mensagem("conversa_reiniciada.txt"))

async def start(message: types.Message):
    db.add_user(message.from_user.id)
    await message.answer_photo(
        photo="https://media-cdn.tripadvisor.com/media/attractions-splice-spp-720x480/12/28/df/5a.jpg",
        caption=carregar_mensagem("bem_vindo.txt"),
        reply_markup=planos.planos_keyboard()
    )

async def handle_plano(callback: types.CallbackQuery):
    logging.info("Pedido de plano por %s", callback.from_user.id)
    valor = float(callback.data.split(":")[1])
    db.set_plano(callback.from_user.id, valor)
    await gerar_cobranca(callback, valor)

async def handle_upsell(callback: types.CallbackQuery):
    await process_custom_plano(callback)

async def handle_remarketing(callback: types.CallbackQuery):
    await process_custom_plano(callback)

async def process_custom_plano(callback: types.CallbackQuery):
    valor = float(callback.data.split(":")[1])
    db.set_plano(callback.from_user.id, valor)
    await gerar_cobranca(callback, valor)

async def gerar_cobranca(callback: types.CallbackQuery, valor: float):
    if PAYMENT_PROVIDER == "hoopay":
        cobranca = await hoopay.criar_cobranca_hoopay(callback.from_user.id, valor)
    elif PAYMENT_PROVIDER == "efi":
        cobranca = await efi.criar_cobranca_efi(callback.from_user.id, valor)
    else:
        cobranca = await mercadopago.criar_cobranca_mercadopago(callback.from_user.id, valor)

    if cobranca and cobranca.get("id"):
        db.update_payment(callback.from_user.id, cobranca["id"], "pending")

        if cobranca.get("link"):
            await callback.message.answer(
                carregar_mensagem("link_pagamento.txt").format(link=cobranca["link"]),
                parse_mode="Markdown"
            )

        await callback.message.answer(carregar_mensagem("pague_com_qrcode.txt"))

        qr_image = criar_qrcode_temp(cobranca.get("qr_code_base64", ""))
        if qr_image:
            await callback.message.answer_photo(photo=qr_image)
        else:
            await callback.message.answer(carregar_mensagem("erro_qrcode.txt"))

        pix_code = cobranca.get("qr_code", "")
        if pix_code:
            PIX_CODES[callback.from_user.id] = pix_code
            await callback.message.answer(
                carregar_mensagem("copiar_pix.txt"),
                reply_markup=copiar_pix_keyboard(pix_code),
                parse_mode="Markdown"
            )

        asyncio.create_task(verificar_pagamento_automaticamente(callback.from_user.id, callback.bot, cobranca["id"]))
    else:
        logging.error(f"Cobrança incompleta: {cobranca}")
        await callback.message.answer(carregar_mensagem("erro_cobranca.txt"))

async def copiar_pix(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    pix_code = PIX_CODES.get(user_id)
    if pix_code:
        await callback.message.answer(
            carregar_mensagem("codigo_pix.txt").format(pix_code=pix_code),
            parse_mode="HTML"
        )
    else:
        await callback.message.answer(carregar_mensagem("erro_codigo_pix.txt"))

async def notificar_dono(bot: Bot, user_id: int, valor: float, gateway: str):
    try:
        texto = carregar_mensagem("venda_realizada.txt").format(user_id=user_id, valor=valor, gateway=gateway)
        await bot.send_message(chat_id=OWNER_ID, text=texto, parse_mode="Markdown")
    except Exception as e:
        logging.exception("Erro ao notificar dono: %s", e)

async def verificar_pagamento_automaticamente(user_id: int, bot: Bot, payment_id: str, tentativas: int = 10):
    for _ in range(tentativas):
        await asyncio.sleep(60)
        if PAYMENT_PROVIDER == "hoopay":
            status = await hoopay.verificar_status_hoopay(payment_id)
        elif PAYMENT_PROVIDER == "efi":
            status = await efi.verificar_status_efi(payment_id)
        else:
            status = await mercadopago.verificar_status_mercadopago(payment_id)

        status_normalizado = normalizar_status(status or "")

        if status_normalizado == "paid":
            db.update_payment(user_id, payment_id, status_normalizado)
            await bot.send_message(user_id, carregar_mensagem("pagamento_confirmado.txt"))
            await agendamento.agendar_upsell(user_id, bot)
            plano_valor = db.get_plano(user_id)
            await notificar_dono(bot, user_id, plano_valor, PAYMENT_PROVIDER)
            return

    await bot.send_message(user_id, carregar_mensagem("pagamento_nao_detectado.txt"))
    db.update_payment(user_id, payment_id, "not_detected")
    asyncio.create_task(agendamento.agendar_remarketing(user_id, bot))

for dp in dispatchers:
    dp.message.register(start, Command("start"))
    dp.message.register(reset_conversation, Command("reset"))
    dp.callback_query.register(handle_plano, F.data.startswith("plano:"))
    dp.callback_query.register(handle_upsell, F.data.startswith("upsell:"))
    dp.callback_query.register(handle_remarketing, F.data.startswith("remarketing:"))
    dp.callback_query.register(copiar_pix, F.data == "copiar_pix")

async def main():
    if PAYMENT_PROVIDER == "efi":
        await efi.inicializar_efi()

    await asyncio.gather(*[dp.start_polling(bot) for dp, bot in zip(dispatchers, bots)])

if __name__ == "__main__":
    asyncio.run(main())
