import asyncio
import os
from dotenv import load_dotenv
from database.init_database import engine, User, Meal, Preset, Food, FoodNutrient
from sqlalchemy import text

load_dotenv()

async def fix_database():
    """Исправляет структуру базы данных"""
    print("🔧 Исправление структуры базы данных...")
    
    async with engine.begin() as conn:
        # Добавляем недостающие колонки
        columns_to_add = [
            "ADD COLUMN IF NOT EXISTS food_name_en VARCHAR",
            "ADD COLUMN IF NOT EXISTS meal_type VARCHAR DEFAULT 'other'",
            "ADD COLUMN IF NOT EXISTS fiber FLOAT DEFAULT 0",
            "ADD COLUMN IF NOT EXISTS sugar FLOAT DEFAULT 0", 
            "ADD COLUMN IF NOT EXISTS sodium FLOAT DEFAULT 0",
            "ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
            "ADD COLUMN IF NOT EXISTS fsm_state VARCHAR",
            "ADD COLUMN IF NOT EXISTS fsm_data JSON"
        ]
        
        for column in columns_to_add:
            try:
                await conn.execute(text(f"ALTER TABLE users {column}"))
                print(f"Добавлена колонка: {column}")
            except Exception as e:
                print(f"Ошибка при добавлении колонки {column}: {e}")
        
        for column in columns_to_add:
            try:
                await conn.execute(text(f"ALTER TABLE meals {column}"))
                print(f"Добавлена колонка в meals: {column}")
            except Exception as e:
                print(f"Ошибка при добавлении колонки в meals {column}: {e}")
        
        # Создаем таблицу daily_stats
        try:
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT REFERENCES users(tg_id),
                    date VARCHAR NOT NULL,
                    total_calories FLOAT DEFAULT 0,
                    total_meals INTEGER DEFAULT 0,
                    water_ml INTEGER DEFAULT 0,
                    mood_score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Таблица daily_stats создана")
        except Exception as e:
            print(f"⚠️ Таблица daily_stats уже существует: {e}")
        
        print("База данных обновлена!")

if __name__ == "__main__":
    asyncio.run(fix_database()) 