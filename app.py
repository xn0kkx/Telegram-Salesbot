import os
from aiogram import Bot, Dispatcher
from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
import asyncio


load_dotenv()


BOT_TOKENS = [
    os.getenv("BOT_TOKEN_1"),
    os.getenv("BOT_TOKEN_2"),
    os.getenv("BOT_TOKEN_3"),
    os.getenv
]

BOT_TOKENS = [token for token in BOT_TOKENS if token] 

bots = [Bot(token) for token in BOT_TOKENS]
dispatchers = [Dispatcher(bot) for bot in bots]

