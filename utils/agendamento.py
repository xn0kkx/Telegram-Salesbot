import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.types import BufferedInputFile
from database import db
from keyboards.upsell import upsell_keyboard
from keyboards.remarketing import remarketing_keyboard

load_dotenv()

MENSAGENS_DIR = "mensagens"
UPSELL_MEDIA = os.getenv("UPSELL_MEDIA", "")
REMARKETING_MEDIA = os.getenv("REMARKETING_MEDIA", "")

def carregar_mensagem(nome_arquivo):
    caminho = os.path.join(MENSAGENS_DIR, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

async def enviar_mensagem(bot: Bot, chat_id: int, texto: str, caminho_midia: str = "", reply_markup=None):
    if caminho_midia and os.path.exists(caminho_midia):
        file_name = os.path.basename(caminho_midia)
        with open(caminho_midia, "rb") as f:
            file_data = f.read()
            if caminho_midia.lower().endswith((".jpg", ".jpeg", ".png")):
                await bot.send_photo(chat_id, photo=BufferedInputFile(file_data, filename=file_name), caption=texto, reply_markup=reply_markup)
            elif caminho_midia.lower().endswith((".mp4", ".mov", ".avi")):
                await bot.send_video(chat_id, video=BufferedInputFile(file_data, filename=file_name), caption=texto, reply_markup=reply_markup)
            else:
                await bot.send_message(chat_id, text=texto, reply_markup=reply_markup)
    else:
        await bot.send_message(chat_id, text=texto, reply_markup=reply_markup)

async def agendar_upsell(user_id: int, bot: Bot):
    await asyncio.sleep(30)
    plano_valor = db.get_plano(user_id)
    teclado = upsell_keyboard(plano_valor)
    if teclado.inline_keyboard:
        await enviar_mensagem(
            bot=bot,
            chat_id=user_id,
            texto=carregar_mensagem("upsell.txt"),
            caminho_midia=UPSELL_MEDIA,
            reply_markup=teclado
        )

async def agendar_remarketing(user_id: int, bot: Bot):
    delays = [120, 300, 600]
    arquivos = [
        "remarketing_1.txt",
        "remarketing_2.txt",
        "remarketing_3.txt"
    ]
    for delay, arquivo in zip(delays, arquivos):
        await asyncio.sleep(delay)
        await enviar_mensagem(
            bot=bot,
            chat_id=user_id,
            texto=carregar_mensagem(arquivo),
            caminho_midia=REMARKETING_MEDIA,
            reply_markup=remarketing_keyboard()
        )
