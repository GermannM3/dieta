#!/usr/bin/env python3
"""
Скрипт для настройки премиум функций
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.init_database import async_session_maker
from sqlalchemy import text

async def setup_premium_functions():
    """Настраивает премиум функции"""
    print("🔧 Настройка премиум функций...")
    
    async with async_session_maker() as session:
        try:
            # Создаем таблицу премиум функций если её нет
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS premium_functions (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    price INTEGER NOT NULL,
                    duration_days INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Добавляем премиум функции
            functions = [
                {
                    "name": "personal_dietitian",
                    "description": "Личный диетолог - индивидуальные консультации и планы питания",
                    "price": 200,
                    "duration_days": 7
                },
                {
                    "name": "menu_generation", 
                    "description": "Генерация персонального меню на неделю",
                    "price": 200,
                    "duration_days": 7
                },
                {
                    "name": "photo_recognition",
                    "description": "Распознавание еды по фото (в разработке)",
                    "price": 0,
                    "duration_days": 0
                }
            ]
            
            for func in functions:
                # Проверяем существует ли функция
                result = await session.execute(
                    text("SELECT id FROM premium_functions WHERE name = :name"),
                    {"name": func["name"]}
                )
                
                if not result.fetchone():
                    await session.execute(text("""
                        INSERT INTO premium_functions (name, description, price, duration_days)
                        VALUES (:name, :description, :price, :duration_days)
                    """), func)
                    print(f"✅ Добавлена функция: {func['name']} - {func['price']}₽")
                else:
                    print(f"ℹ️  Функция уже существует: {func['name']}")
            
            await session.commit()
            print("✅ Настройка премиум функций завершена!")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(setup_premium_functions()) 