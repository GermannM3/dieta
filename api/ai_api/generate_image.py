from urllib.parse import quote
import random
import re
import sys
import asyncio
sys.path.append('..')
from api.ai_api.generate_text import translate


async def image_generator(prompt: str):
    # Если prompt содержит кириллицу — переводим на английский
    if re.search(r'[а-яА-ЯёЁ]', prompt):
        prompt = await translate(prompt, source_lang='ru', target_lang='en')
    parsed_prompt = quote(prompt.replace(' ', '+'))
    seed = random.randint(1,999999)
    image_url = f'https://image.pollinations.ai/prompt/{parsed_prompt}?seed={seed}&width=1024&height=1024&model=dall-e-3&nologo=true&private=false&enhance=false&safe=false'
    return image_url