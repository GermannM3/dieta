#!/usr/bin/env python3
"""
Скрипт для исправления админа в базе данных
"""

import os
import sys
import asyncio
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.init_database import engine, WebUser, async_session
from passlib.context import CryptContext

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return pwd_context.hash(password)

async def fix_admin():
    """Исправляет админа в базе данных"""
    print("🔧 Исправляем админа...")
    
    async with async_session() as session:
        try:
            # Проверяем существует ли админ
            admin_email = "admin@dieta.ru"
            
            # Ищем существующего админа
            result = await session.execute(
                "SELECT id, email FROM web_users WHERE email = :email",
                {"email": admin_email}
            )
            existing_admin = result.fetchone()
            
            if existing_admin:
                print(f"❌ Админ уже существует: {existing_admin[1]}")
                # Удаляем старого админа
                await session.execute(
                    "DELETE FROM web_users WHERE email = :email",
                    {"email": admin_email}
                )
                await session.commit()
                print("🗑️ Старый админ удален")
            
            # Создаем нового админа
            hashed_password = hash_password("admin123")
            
            await session.execute(
                """
                INSERT INTO web_users (email, password_hash, name, is_confirmed, created_at, updated_at)
                VALUES (:email, :password_hash, :name, :is_confirmed, NOW(), NOW())
                """,
                {
                    "email": admin_email,
                    "password_hash": hashed_password,
                    "name": "Администратор",
                    "is_confirmed": True
                }
            )
            
            await session.commit()
            
            print(f"✅ Новый админ создан: {admin_email}")
            print("🔑 Логин: admin@dieta.ru")
            print("🔑 Пароль: admin123")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await session.rollback()
            raise

async def main():
    """Главная функция"""
    try:
        await fix_admin()
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 