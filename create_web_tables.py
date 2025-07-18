#!/usr/bin/env python3
"""
Создание таблиц для веб-аутентификации в Neon PostgreSQL
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from database.init_database import Base

load_dotenv()

async def create_web_tables():
    """Создание таблиц для веб-пользователей"""
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL не найден в .env!")
        return False
    
    print("🔧 Создание таблиц для веб-аутентификации...")
    print(f"📊 База данных: {DATABASE_URL[:50]}...")
    
    try:
        # Создаем engine
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        # SQL для создания таблиц
        create_tables_sql = """
        -- Таблица веб-пользователей
        CREATE TABLE IF NOT EXISTS web_users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(100),
            is_confirmed BOOLEAN DEFAULT FALSE,
            confirmation_code VARCHAR(10),
            reset_code VARCHAR(10),
            reset_code_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Индекс для email
        CREATE INDEX IF NOT EXISTS idx_web_users_email ON web_users(email);

        -- Таблица профилей веб-пользователей
        CREATE TABLE IF NOT EXISTS web_profiles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES web_users(id) ON DELETE CASCADE,
            name VARCHAR(100),
            gender VARCHAR(10) CHECK (gender IN ('male', 'female')),
            age INTEGER CHECK (age > 0 AND age < 150),
            weight DECIMAL(5,2) CHECK (weight > 0),
            height DECIMAL(5,2) CHECK (height > 0),
            activity_level DECIMAL(3,2) CHECK (activity_level >= 1.0 AND activity_level <= 3.0),
            daily_target DECIMAL(7,2),
            water_target INTEGER DEFAULT 2000,
            steps_target INTEGER DEFAULT 10000,
            mood VARCHAR(20) CHECK (mood IN ('excellent', 'good', 'okay', 'bad', 'terrible')),
            water_ml INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            score INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Индекс для user_id
        CREATE INDEX IF NOT EXISTS idx_web_profiles_user_id ON web_profiles(user_id);

        -- Таблица приемов пищи веб-пользователей
        CREATE TABLE IF NOT EXISTS web_meals (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES web_users(id) ON DELETE CASCADE,
            date VARCHAR(10) NOT NULL, -- YYYY-MM-DD
            time VARCHAR(8), -- HH:MM:SS
            food_name VARCHAR(200) NOT NULL,
            weight_grams DECIMAL(7,2) NOT NULL CHECK (weight_grams > 0),
            calories DECIMAL(7,2) NOT NULL CHECK (calories >= 0),
            protein DECIMAL(7,2) DEFAULT 0,
            fat DECIMAL(7,2) DEFAULT 0,
            carbs DECIMAL(7,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Индексы для web_meals
        CREATE INDEX IF NOT EXISTS idx_web_meals_user_id ON web_meals(user_id);
        CREATE INDEX IF NOT EXISTS idx_web_meals_date ON web_meals(date);
        CREATE INDEX IF NOT EXISTS idx_web_meals_user_date ON web_meals(user_id, date);

        -- Таблица пресетов веб-пользователей
        CREATE TABLE IF NOT EXISTS web_presets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES web_users(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            meal_type VARCHAR(20) CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
            food_items JSONB NOT NULL,
            total_calories DECIMAL(7,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Индекс для web_presets
        CREATE INDEX IF NOT EXISTS idx_web_presets_user_id ON web_presets(user_id);
        """
        
        async with engine.begin() as conn:
            print("📝 Выполнение SQL запросов...")
            await conn.execute(text(create_tables_sql))
            print("✅ Таблицы созданы успешно!")
        
        # Проверяем созданные таблицы
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'web_%'
                ORDER BY table_name;
            """))
            
            tables = result.fetchall()
            print("\n📋 Созданные таблицы:")
            for table in tables:
                print(f"  ✅ {table[0]}")
        
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")
        return False

async def main():
    print("🗄️ Настройка базы данных для веб-аутентификации")
    print("=" * 50)
    
    success = await create_web_tables()
    
    if success:
        print("\n🎉 База данных готова!")
        print("✅ Веб-аутентификация настроена")
        print("✅ Таблицы пользователей созданы")
        print("✅ Можно тестировать регистрацию")
    else:
        print("\n❌ Ошибка настройки базы данных")

if __name__ == "__main__":
    asyncio.run(main()) 