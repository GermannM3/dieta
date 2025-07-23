#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения к базе данных
"""
import asyncio
import os
from dotenv import load_dotenv
from database.init_database import engine, init_db
from sqlalchemy import text

load_dotenv()

async def test_db_connection():
    """Тестирует подключение к базе данных"""
    print("Testing database connection...")
    
    try:
        # Проверяем переменные окружения
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("ERROR: DATABASE_URL not found in environment variables")
            return False
        
        print(f"OK: DATABASE_URL found: {database_url[:50]}...")
        
        # Тестируем подключение
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("OK: Database connection successful")
            
            # Проверяем существование таблиц
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'meals', 'presets')
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"OK: Found tables: {tables}")
            
        return True
        
    except Exception as e:
        print(f"ERROR: Database connection error: {e}")
        return False

async def test_bot_startup():
    """Тестирует инициализацию бота"""
    print("\nTesting bot initialization...")
    
    try:
        # Проверяем токен бота
        tg_token = os.getenv('TG_TOKEN')
        if not tg_token:
            print("ERROR: TG_TOKEN not found in environment variables")
            return False
        
        print(f"OK: TG_TOKEN found: {tg_token[:20]}...")
        
        # Инициализируем базу данных
        await init_db()
        print("OK: Database initialized")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Bot initialization error: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("=" * 50)
    print("TESTING CONNECTIONS")
    print("=" * 50)
    
    # Тестируем подключение к БД
    db_ok = await test_db_connection()
    
    # Тестируем инициализацию бота
    bot_ok = await test_bot_startup()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Database: {'OK' if db_ok else 'FAIL'}")
    print(f"Bot initialization: {'OK' if bot_ok else 'FAIL'}")
    
    if db_ok and bot_ok:
        print("\nAll tests passed! Bot should start successfully.")
    else:
        print("\nThere are issues that need to be fixed.")
    
    # Закрываем соединения
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main()) 