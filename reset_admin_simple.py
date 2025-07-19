#!/usr/bin/env python3
"""
Простой скрипт для сброса пароля администратора
"""

import asyncio
import sys
import os
import bcrypt

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select
from database.init_database import async_session, WebUser

async def reset_admin_password():
    """Сброс пароля администратора"""
    print("🔧 Сброс пароля администратора")
    print("=" * 50)
    
    # Данные администратора
    admin_email = "germannm@vk.com"
    new_password = "admin123"  # Простой пароль для тестирования
    
    try:
        async with async_session() as session:
            # Находим пользователя
            result = await session.execute(
                select(WebUser).where(WebUser.email == admin_email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ Пользователь с email {admin_email} не найден")
                print("🔧 Создаем нового админа...")
                
                # Создаем нового админа
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
                return
            
            # Хешируем новый пароль
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Обновляем пароль
            user.password_hash = password_hash
            user.is_confirmed = True  # Подтверждаем email
            
            await session.commit()
            
            print(f"✅ Пароль для {admin_email} обновлен")
            print(f"📧 Email: {admin_email}")
            print(f"🔑 Новый пароль: {new_password}")
            print("⚠️  Не забудьте сменить пароль после входа!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("🔧 Проверьте подключение к базе данных")

if __name__ == "__main__":
    asyncio.run(reset_admin_password()) 