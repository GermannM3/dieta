import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums.parse_mode import ParseMode
from dotenv import load_dotenv

load_dotenv()

_token = os.getenv("TG_TOKEN")
_proxy = os.getenv("TG_PROXY", "").strip()

if _proxy:
    _session = AiohttpSession(proxy=_proxy)
    bot = Bot(_token, session=_session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
else:
    bot = Bot(_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
