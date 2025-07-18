#!/usr/bin/env python3
"""
Создание администратора для веб-приложения
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select
from database.init_database import async_session, WebUser, WebProfile
from api.auth_api import hash_password

load_dotenv()

async def create_admin_user():
    """Создание администратора"""
    
    print("🔧 Создание администратора...")
    
    try:
        async with async_session() as session:
            # Проверяем, существует ли уже администратор
            result = await session.execute(
                select(WebUser).where(WebUser.email == 'germannm@vk.com')
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print("✅ Администратор уже существует")
                
                # Проверяем профиль
                profile_result = await session.execute(
                    select(WebProfile).where(WebProfile.user_id == existing_admin.id)
                )
                profile = profile_result.scalar_one_or_none()
                
                if not profile:
                    print("📝 Создаем профиль для администратора...")
                    profile = WebProfile(
                        user_id=existing_admin.id,
                        name="Администратор",
                        is_premium=True
                    )
                    session.add(profile)
                    await session.commit()
                    print("✅ Профиль администратора создан")
                else:
                    print("✅ Профиль администратора уже существует")
                
                return True
            
            # Создаем нового администратора
            print("📝 Создаем нового администратора...")
            
            # Хешируем пароль
            password_hash = hash_password("Germ@nnM3")
            
            # Создаем пользователя
            admin_user = WebUser(
                email='germannm@vk.com',
                password_hash=password_hash,
                name='Администратор',
                is_confirmed=True  # Подтверждаем email автоматически
            )
            session.add(admin_user)
            await session.flush()  # Получаем ID пользователя
            
            # Создаем профиль
            admin_profile = WebProfile(
                user_id=admin_user.id,
                name="Администратор",
                is_premium=True,  # Администратор имеет премиум
                score=1000,  # Высокий рейтинг
                streak_days=365  # Максимальный стрик
            )
            session.add(admin_profile)
            
            await session.commit()
            
            print("✅ Администратор создан успешно!")
            print(f"📧 Email: germannm@vk.com")
            print(f"🔑 Пароль: Germ@nnM3")
            print(f"👤 ID: {admin_user.id}")
            print(f"💎 Премиум: активирован")
            
            return True
            
    except Exception as e:
        print(f"❌ Ошибка создания администратора: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("👑 Настройка администратора веб-приложения")
    print("=" * 50)
    
    success = await create_admin_user()
    
    if success:
        print("\n🎉 Администратор готов!")
        print("✅ Можете войти в веб-приложение")
        print("✅ Админ-панель будет доступна после входа")
    else:
        print("\n❌ Ошибка создания администратора")

if __name__ == "__main__":
    asyncio.run(main()) 