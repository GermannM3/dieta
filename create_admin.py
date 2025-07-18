#!/usr/bin/env python3
"""
Скрипт для создания администратора
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.init_database import async_session, WebUser, WebProfile
from api.auth_api import register_user, UserRegister

load_dotenv()

async def create_admin():
    """Создание администратора"""
    print("🔧 Создание администратора")
    print("=" * 50)
    
    admin_email = "germannm@vk.com"
    admin_password = "Germ@nnM3"
    admin_name = "Администратор"
    
    try:
        async with async_session() as session:
            # Проверяем, существует ли уже администратор
            result = await session.execute(
                f"SELECT id FROM web_users WHERE email = '{admin_email}'"
            )
            existing_user = result.fetchone()
            
            if existing_user:
                print(f"⚠️ Администратор с email {admin_email} уже существует")
                
                # Обновляем профиль администратора
                profile_result = await session.execute(
                    f"SELECT id FROM web_profiles WHERE user_id = {existing_user[0]}"
                )
                existing_profile = profile_result.fetchone()
                
                if existing_profile:
                    # Обновляем профиль
                    await session.execute(
                        f"UPDATE web_profiles SET is_premium = true WHERE user_id = {existing_user[0]}"
                    )
                    print("✅ Профиль администратора обновлен (is_premium = true)")
                else:
                    # Создаем профиль
                    await session.execute(
                        f"INSERT INTO web_profiles (user_id, name, is_premium) VALUES ({existing_user[0]}, '{admin_name}', true)"
                    )
                    print("✅ Профиль администратора создан")
                
                await session.commit()
                return
            
            # Создаем нового администратора
            print(f"📝 Создание администратора: {admin_email}")
            
            # Создаем пользователя через функцию регистрации
            user_data = UserRegister(
                email=admin_email,
                password=admin_password,
                name=admin_name
            )
            
            # Регистрируем пользователя
            auth_response = await register_user(user_data)
            
            if auth_response:
                print(f"✅ Пользователь создан с ID: {auth_response.user.id}")
                
                # Создаем профиль администратора
                profile = WebProfile(
                    user_id=auth_response.user.id,
                    name=admin_name,
                    is_premium=True
                )
                session.add(profile)
                await session.commit()
                
                print("✅ Профиль администратора создан")
                print("✅ Администратор успешно создан!")
                print(f"  Email: {admin_email}")
                print(f"  Пароль: {admin_password}")
                print(f"  Премиум: активен")
                print(f"  Сообщение: {auth_response.message}")
                
            else:
                print("❌ Ошибка создания пользователя")
                
    except Exception as e:
        print(f"❌ Ошибка создания администратора: {e}")
        import traceback
        traceback.print_exc()

async def test_admin_login():
    """Тест входа администратора"""
    print("\n🧪 Тест входа администратора")
    print("=" * 50)
    
    try:
        from api.auth_api import login_user, UserLogin
        
        admin_email = "germannm@vk.com"
        admin_password = "Germ@nnM3"
        
        login_data = UserLogin(email=admin_email, password=admin_password)
        auth_response = await login_user(login_data)
        
        if auth_response:
            print("✅ Вход администратора успешен")
            print(f"  ID: {auth_response.user.id}")
            print(f"  Email: {auth_response.user.email}")
            print(f"  Подтвержден: {auth_response.user.is_confirmed}")
            print(f"  Токен: {auth_response.token[:20]}...")
        else:
            print("❌ Ошибка входа администратора")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования входа: {e}")

if __name__ == "__main__":
    async def main():
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == "create":
                await create_admin()
            elif command == "test":
                await test_admin_login()
            else:
                print("Использование:")
                print("  python create_admin.py create - создать администратора")
                print("  python create_admin.py test   - протестировать вход")
        else:
            await create_admin()
            await test_admin_login()
    
    asyncio.run(main()) 