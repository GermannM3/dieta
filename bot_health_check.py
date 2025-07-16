#!/usr/bin/env python3
"""
Скрипт для проверки здоровья Telegram бота
Отправляет тестовое сообщение администратору для проверки активности
"""

import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

from core.init_bot import bot

async def health_check():
    """Проверка здоровья бота"""
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        print(f"✅ Бот активен: @{bot_info.username} ({bot_info.full_name})")
        
        # Получаем ID администратора
        admin_id = os.getenv('ADMIN_ID')
        if not admin_id:
            print("❌ ADMIN_ID не настроен в .env")
            return False
            
        # Отправляем тестовое сообщение администратору
        timestamp = datetime.now().strftime("%H:%M:%S %d.%m.%Y")
        test_message = f"🔍 <b>Проверка активности бота</b>\n\n" \
                      f"⏰ Время: {timestamp}\n" \
                      f"✅ Статус: Активен\n" \
                      f"🤖 Бот: @{bot_info.username}\n\n" \
                      f"<i>Автоматическая проверка здоровья</i>"
        
        await bot.send_message(
            chat_id=int(admin_id),
            text=test_message,
            parse_mode='HTML'
        )
        
        print(f"✅ Тестовое сообщение отправлено администратору (ID: {admin_id})")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки здоровья: {e}")
        return False
    finally:
        await bot.session.close()

async def ping_test():
    """Простой ping тест"""
    try:
        bot_info = await bot.get_me()
        print(f"🏓 Ping успешен: {bot_info.username}")
        return True
    except Exception as e:
        print(f"💥 Ping неудачен: {e}")
        return False
    finally:
        await bot.session.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "ping":
        # Простой ping без отправки сообщений
        result = asyncio.run(ping_test())
    else:
        # Полная проверка здоровья
        result = asyncio.run(health_check())
    
    sys.exit(0 if result else 1) 