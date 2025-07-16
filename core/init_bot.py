from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv

import os

load_dotenv()

bot = Bot(os.getenv('TG_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
