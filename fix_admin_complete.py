#!/usr/bin/env python3
"""
Полное исправление администратора
"""

import asyncio
import sys
import os
import bcrypt

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select, delete
from database.init_database import async_session, WebUser

async def fix_admin_complete():
    """Полное исправление администратора"""
    print("🔧 Полное исправление администратора")
    print("=" * 50)
    
    # Данные администратора
    admin_email = "germannm@vk.com"
    new_password = "admin123"
    
    try:
        async with async_session() as session:
            # 1. Удаляем старого админа если есть
            await session.execute(
                delete(WebUser).where(WebUser.email == admin_email)
            )
            await session.commit()
            print("🗑️  Старый админ удален")
            
            # 2. Создаем нового админа с правильным хешем
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            new_admin = WebUser(
                email=admin_email,
                password_hash=password_hash,
                name="Администратор",
                is_confirmed=True,
                confirmation_code=None
            )
            
            session.add(new_admin)
            await session.commit()
            await session.refresh(new_admin)
            
            print(f"✅ Создан новый администратор")
            print(f"📧 Email: {admin_email}")
            print(f"🔑 Пароль: {new_password}")
            print(f"🔐 Хеш: {password_hash[:20]}...")
            
            # 3. Проверяем что хеш работает
            test_check = bcrypt.checkpw(new_password.encode('utf-8'), password_hash.encode('utf-8'))
            print(f"✅ Проверка хеша: {'OK' if test_check else 'FAIL'}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_admin_complete()) 