#!/usr/bin/env python3
import asyncio
import bcrypt
from database.init_database import async_session_maker
from sqlalchemy import text

async def fix_admin():
    print("🔧 Исправление админа germannm@vk.com...")
    
    # Хешируем пароль
    password = "Germ@nnM3"
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    async with async_session_maker() as session:
        try:
            # Проверяем существует ли пользователь
            result = await session.execute(
                text("SELECT id, email, is_admin FROM users WHERE email = :email"),
                {"email": "germannm@vk.com"}
            )
            user = result.fetchone()
            
            if user:
                print(f"✅ Пользователь найден: {user.email}")
                
                # Обновляем пароль и делаем админом
                await session.execute(
                    text("""
                        UPDATE users 
                        SET password_hash = :password_hash, 
                            is_admin = true,
                            is_verified = true
                        WHERE email = :email
                    """),
                    {
                        "password_hash": hashed_password.decode('utf-8'),
                        "email": "germannm@vk.com"
                    }
                )
                print("✅ Пароль обновлен и пользователь сделан админом")
            else:
                print("❌ Пользователь не найден, создаем нового...")
                
                # Создаем нового админа
                await session.execute(
                    text("""
                        INSERT INTO users (email, password_hash, is_admin, is_verified, created_at)
                        VALUES (:email, :password_hash, true, true, NOW())
                    """),
                    {
                        "email": "germannm@vk.com",
                        "password_hash": hashed_password.decode('utf-8')
                    }
                )
                print("✅ Новый админ создан")
            
            await session.commit()
            print("✅ Изменения сохранены в базе")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(fix_admin()) 