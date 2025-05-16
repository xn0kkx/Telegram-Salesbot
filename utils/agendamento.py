import asyncio
import os
from aiogram import Bot
from database import db
from keyboards.upsell import upsell_keyboard
from keyboards.remarketing import remarketing_keyboard

MENSAGENS_DIR = "mensagens"

def carregar_mensagem(nome_arquivo):
    caminho = os.path.join(MENSAGENS_DIR, nome_arquivo)
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

async def agendar_upsell(user_id: int, bot: Bot):
    await asyncio.sleep(30)
    plano_valor = db.get_plano(user_id)
    teclado = upsell_keyboard(plano_valor)
    if teclado.inline_keyboard:
        await bot.send_message(
            chat_id=user_id,
            text=carregar_mensagem("upsell.txt"),
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
        await bot.send_message(
            chat_id=user_id,
            text=carregar_mensagem(arquivo),
            reply_markup=remarketing_keyboard()
        )