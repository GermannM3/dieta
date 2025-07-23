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
from database.crud import get_user_by_tg_id
from sqlalchemy import text

async def activate_premium_for_admin():
    """Активирует премиум для админа"""
    print("🔧 Активация премиума для админа...")
    
    admin_tg_id = 389694638
    
    async with async_session_maker() as session:
        try:
            # Проверяем существующего пользователя
            user = await get_user_by_tg_id(session, admin_tg_id)
            
            if user:
                print(f"✅ Пользователь найден: {user.name}")
                
                # Активируем премиум
                user.is_premium = True
                await session.commit()
                
                print(f"✅ Премиум активирован для пользователя {user.name}")
                print(f"   is_premium: {user.is_premium}")
            else:
                print(f"❌ Пользователь с tg_id {admin_tg_id} не найден")
                
                # Создаем пользователя с премиумом
                result = await session.execute(
                    text(f"""
                    INSERT INTO users (tg_id, name, is_premium) 
                    VALUES ({admin_tg_id}, 'Admin', true)
                    ON CONFLICT (tg_id) 
                    DO UPDATE SET is_premium = true
                    RETURNING *
                    """)
                )
                await session.commit()
                
                print(f"✅ Создан новый пользователь с премиумом")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(activate_premium_for_admin()) 