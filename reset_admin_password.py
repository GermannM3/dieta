#!/usr/bin/env python3
"""
Скрипт для сброса пароля администратора
"""

import asyncio
import bcrypt
from sqlalchemy import select
from database.init_database import async_session
from database.models import WebUser

async def reset_admin_password():
    """Сброс пароля администратора"""
    print("🔧 Сброс пароля администратора")
    print("=" * 50)
    
    # Данные администратора
    admin_email = "germannm@vk.com"
    new_password = "admin123"  # Простой пароль для тестирования
    
    async with async_session() as session:
        # Находим пользователя
        result = await session.execute(
            select(WebUser).where(WebUser.email == admin_email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ Пользователь с email {admin_email} не найден")
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

if __name__ == "__main__":
    asyncio.run(reset_admin_password()) 