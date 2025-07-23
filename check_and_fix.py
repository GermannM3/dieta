#!/usr/bin/env python3
"""
Скрипт для проверки и исправления всех проблем в проекте
"""
import os
import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Проверяет версию Python"""
    print("🐍 Проверка версии Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Требуется Python 3.8+, текущая версия: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def check_dependencies():
    """Проверяет установленные зависимости"""
    print("\n📦 Проверка зависимостей...")
    
    required_packages = [
        'aiogram',
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'asyncpg',
        'dotenv',
        'requests',
        'yookassa',
        'mistralai',
        'aiofiles',
        'psutil'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - НЕ УСТАНОВЛЕН")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("Установите их командой: pip install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Проверяет наличие и содержимое .env файла"""
    print("\n🔧 Проверка .env файла...")
    
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ Файл .env не найден")
        return False
    
    # Загружаем переменные окружения
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'TG_TOKEN',
        'DATABASE_URL',
        'MISTRAL_API_KEY',
        'GIGACHAT_CLIENT_ID',
        'GIGACHAT_AUTH_KEY',
        'YOOKASSA_SHOP_ID',
        'YOOKASSA_SECRET_KEY'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            print(f"❌ {var} - НЕ НАЙДЕН")
            missing_vars.append(var)
        else:
            # Скрываем чувствительные данные
            if 'TOKEN' in var or 'KEY' in var or 'PASSWORD' in var:
                masked_value = value[:10] + '...' if len(value) > 10 else '***'
                print(f"✅ {var} - {masked_value}")
            else:
                print(f"✅ {var} - {value}")
    
    if missing_vars:
        print(f"\n⚠️  Отсутствуют переменные: {', '.join(missing_vars)}")
        return False
    
    return True

def check_database_connection():
    """Проверяет подключение к базе данных"""
    print("\n🗄️  Проверка подключения к базе данных...")
    
    try:
        from database.init_database import engine
        from sqlalchemy import text
        
        import asyncio
        
        async def test_connection():
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                return True
        
        asyncio.run(test_connection())
        print("✅ Подключение к базе данных - OK")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

def check_bot_token():
    """Проверяет токен бота"""
    print("\n🤖 Проверка токена бота...")
    
    try:
        from core.init_bot import bot
        
        import asyncio
        
        async def test_bot():
            bot_info = await bot.get_me()
            print(f"✅ Бот подключен: @{bot_info.username} ({bot_info.full_name})")
            return True
        
        asyncio.run(test_bot())
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к боту: {e}")
        return False

def check_yookassa_config():
    """Проверяет конфигурацию YooKassa"""
    print("\n💳 Проверка конфигурации YooKassa...")
    
    try:
        from yookassa import Configuration
        
        shop_id = os.getenv('YOOKASSA_SHOP_ID')
        secret_key = os.getenv('YOOKASSA_SECRET_KEY')
        
        if not shop_id or not secret_key:
            print("❌ Отсутствуют ключи YooKassa")
            return False
        
        # Тестируем конфигурацию
        Configuration.account_id = shop_id
        Configuration.secret_key = secret_key
        
        print(f"✅ YooKassa настроен: Shop ID {shop_id}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конфигурации YooKassa: {e}")
        return False

def check_file_structure():
    """Проверяет структуру файлов"""
    print("\n📁 Проверка структуры файлов...")
    
    required_files = [
        'main.py',
        'improved_api_server.py',
        'start_all_services.py',
        'requirements.txt',
        'database/init_database.py',
        'core/init_bot.py',
        'components/payment_system/payment_operations.py',
        'components/payment_system/payment_handlers.py',
        'utils/logger.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} - OK")
        else:
            print(f"❌ {file_path} - НЕ НАЙДЕН")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    return True

def check_syntax():
    """Проверяет синтаксис Python файлов"""
    print("\n🔍 Проверка синтаксиса...")
    
    python_files = [
        'main.py',
        'improved_api_server.py',
        'start_all_services.py',
        'database/init_database.py',
        'core/init_bot.py',
        'components/payment_system/payment_operations.py',
        'components/payment_system/payment_handlers.py',
        'utils/logger.py'
    ]
    
    syntax_errors = []
    
    for file_path in python_files:
        if Path(file_path).exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    compile(f.read(), file_path, 'exec')
                print(f"✅ {file_path} - синтаксис OK")
            except SyntaxError as e:
                print(f"❌ {file_path} - синтаксическая ошибка: {e}")
                syntax_errors.append(file_path)
    
    if syntax_errors:
        print(f"\n⚠️  Синтаксические ошибки в файлах: {', '.join(syntax_errors)}")
        return False
    
    return True

def run_tests():
    """Запускает тесты"""
    print("\n🧪 Запуск тестов...")
    
    try:
        # Тест подключения к БД
        result = subprocess.run([sys.executable, 'test_db_connection.py'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Тест подключения к БД - OK")
            return True
        else:
            print(f"❌ Тест подключения к БД - FAIL")
            print(f"Ошибка: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Тест подключения к БД - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ Ошибка запуска тестов: {e}")
        return False

def main():
    """Главная функция проверки"""
    print("=" * 60)
    print("🔍 ПРОВЕРКА ПРОЕКТА DIETA BOT")
    print("=" * 60)
    
    checks = [
        ("Версия Python", check_python_version),
        ("Структура файлов", check_file_structure),
        ("Синтаксис", check_syntax),
        ("Переменные окружения", check_env_file),
        ("Зависимости", check_dependencies),
        ("Подключение к БД", check_database_connection),
        ("Токен бота", check_bot_token),
        ("Конфигурация YooKassa", check_yookassa_config),
        ("Тесты", run_tests)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Ошибка в проверке {check_name}: {e}")
            results.append((check_name, False))
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nИтого: {passed} прошло, {failed} не прошло")
    
    if failed == 0:
        print("\n🎉 Все проверки пройдены! Проект готов к работе.")
        return True
    else:
        print(f"\n⚠️  Найдено {failed} проблем. Исправьте их перед запуском.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 