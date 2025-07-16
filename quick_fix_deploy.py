#!/usr/bin/env python3
"""
Быстрое исправление проблем с БД и деплой
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_database_connection():
    """Проверка подключения к базе данных"""
    try:
        from database.init_database import engine, init_db
        from sqlalchemy import text
        
        logger.info("🔍 Проверка подключения к базе данных...")
        
        # Попытка подключения
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("✅ База данных доступна!")
            
        # Инициализация таблиц
        logger.info("🏗️ Инициализация таблиц...")
        await init_db()
        logger.info("✅ Таблицы готовы!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к БД: {e}")
        return False

def check_environment():
    """Проверка переменных окружения"""
    logger.info("🔍 Проверка переменных окружения...")
    
    load_dotenv()
    
    required_vars = [
        'TG_TOKEN',
        'DATABASE_URL',
        'MISTRAL_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
        logger.info("💡 Создайте файл .env на основе env.example")
        return False
    
    logger.info("✅ Все необходимые переменные окружения настроены!")
    return True

def check_dependencies():
    """Проверка зависимостей"""
    logger.info("🔍 Проверка зависимостей...")
    
    # Список пакетов с их import именами
    required_packages = [
        ('aiogram', 'aiogram'),
        ('sqlalchemy', 'sqlalchemy'),
        ('asyncpg', 'asyncpg'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('python-dotenv', 'dotenv'),
        ('requests', 'requests')
    ]
    
    missing_packages = []
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        logger.error(f"❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
        logger.info("💡 Установите: pip install -r requirements.txt")
        return False
    
    logger.info("✅ Все зависимости установлены!")
    return True

async def main():
    """Основная функция диагностики и исправления"""
    logger.info("🚀 Быстрая диагностика системы диетолог-бота")
    logger.info("=" * 60)
    
    # Проверка переменных окружения
    if not check_environment():
        logger.error("🛑 Остановка: проблемы с конфигурацией")
        return False
    
    # Проверка зависимостей
    if not check_dependencies():
        logger.error("🛑 Остановка: проблемы с зависимостями")
        return False
    
    # Проверка БД
    if not await check_database_connection():
        logger.error("🛑 Остановка: проблемы с базой данных")
        logger.info("💡 Решения:")
        logger.info("   1. Проверьте DATABASE_URL в .env")
        logger.info("   2. Убедитесь что БД доступна")
        logger.info("   3. Для Neon.tech проверьте статус сервиса")
        return False
    
    logger.info("🎉 Все проверки пройдены успешно!")
    logger.info("✅ Система готова к запуску")
    
    # Запуск сервисов
    logger.info("\n🚀 Запуск системы...")
    logger.info("Используйте: python start_all_services.py")
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if not result:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 Операция прервана пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        sys.exit(1) 