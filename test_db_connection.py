#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подключения к базе данных
"""
import asyncio
import os
from dotenv import load_dotenv
from database.init_database import engine, init_db

load_dotenv()

async def test_db_connection():
    """Тестирует подключение к базе данных"""
    print("🔍 Тестирование подключения к базе данных...")
    
    try:
        # Проверяем переменные окружения
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL не найден в переменных окружения")
            return False
        
        print(f"✅ DATABASE_URL найден: {database_url[:50]}...")
        
        # Тестируем подключение
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            print("✅ Подключение к базе данных успешно")
            
            # Проверяем существование таблиц
            result = await conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'meals', 'presets')
            """)
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Найдены таблицы: {tables}")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False

async def test_bot_startup():
    """Тестирует инициализацию бота"""
    print("\n🤖 Тестирование инициализации бота...")
    
    try:
        # Проверяем токен бота
        tg_token = os.getenv('TG_TOKEN')
        if not tg_token:
            print("❌ TG_TOKEN не найден в переменных окружения")
            return False
        
        print(f"✅ TG_TOKEN найден: {tg_token[:20]}...")
        
        # Инициализируем базу данных
        await init_db()
        print("✅ База данных инициализирована")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка инициализации бота: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("=" * 50)
    print("🧪 ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЙ")
    print("=" * 50)
    
    # Тестируем подключение к БД
    db_ok = await test_db_connection()
    
    # Тестируем инициализацию бота
    bot_ok = await test_bot_startup()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 50)
    print(f"База данных: {'✅ OK' if db_ok else '❌ FAIL'}")
    print(f"Инициализация бота: {'✅ OK' if bot_ok else '❌ FAIL'}")
    
    if db_ok and bot_ok:
        print("\n🎉 Все тесты пройдены! Бот должен запуститься успешно.")
    else:
        print("\n⚠️  Есть проблемы, которые нужно исправить.")
    
    # Закрываем соединения
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main()) 