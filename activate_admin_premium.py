#!/usr/bin/env python3
"""
Скрипт для активации премиума для админа
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.init_database import async_session_maker
from database.crud import get_user_by_tg_id, get_user_by_email
from sqlalchemy import text

async def activate_admin_premium():
    """Активирует премиум для админа"""
    print("🔧 Активация премиума для админа...")
    
    admin_tg_id = 389694638
    admin_email = "germannm@vk.com"
    
    async with async_session_maker() as session:
        try:
            # Проверяем Telegram пользователя
            tg_user = await get_user_by_tg_id(session, admin_tg_id)
            
            if tg_user:
                print(f"✅ Telegram пользователь найден: {tg_user.name}")
                tg_user.is_premium = True
                print("✅ Премиум для Telegram активирован")
            else:
                print("❌ Telegram пользователь не найден")
            
            # Проверяем веб пользователя
            web_user = await get_user_by_email(session, admin_email)
            
            if web_user:
                print(f"✅ Веб пользователь найден: {web_user.name}")
                web_user.is_premium = True
                print("✅ Премиум для веб активирован")
            else:
                print("❌ Веб пользователь не найден")
            
            await session.commit()
            print("✅ Все изменения сохранены!")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(activate_admin_premium()) 