#!/usr/bin/env python3
"""
Скрипт для проверки и исправления всех проблем
"""

import os
import sys
import requests
import json
from datetime import datetime

def check_api_url():
    """Проверяет API URL в файлах"""
    print("🔍 Проверка API URL...")
    
    # Проверяем user_handlers.py
    with open('components/handlers/user_handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'http://5.129.198.80:8000' in content:
            print("✅ API URL в user_handlers.py корректен")
        else:
            print("❌ API URL в user_handlers.py НЕ корректен")
            return False
    
    return True

def check_api_endpoints():
    """Проверяет наличие endpoint'ов в API"""
    print("\n🔍 Проверка API endpoints...")
    
    # Проверяем improved_api_server.py
    with open('improved_api_server.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if '@app.post("/api/add_preset_meals")' in content:
            print("✅ Endpoint /api/add_preset_meals найден")
        else:
            print("❌ Endpoint /api/add_preset_meals НЕ найден")
            return False
    
    return True

def check_payment_system():
    """Проверяет платежную систему"""
    print("\n🔍 Проверка платежной системы...")
    
    # Проверяем payment_handlers.py
    with open('components/payment_system/payment_handlers.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'diet_consultant_handler' in content and 'menu_generator_handler' in content:
            print("✅ Платежные обработчики найдены")
        else:
            print("❌ Платежные обработчики НЕ найдены")
            return False
    
    # Проверяем main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'payment_router' in content:
            print("✅ Payment router подключен в main.py")
        else:
            print("❌ Payment router НЕ подключен в main.py")
            return False
    
    return True

def test_api_connection():
    """Тестирует подключение к API"""
    print("\n🔍 Тестирование подключения к API...")
    
    try:
        # Тестируем health endpoint
        response = requests.get('http://5.129.198.80:8000/health', timeout=10)
        if response.status_code == 200:
            print("✅ API доступен по адресу http://5.129.198.80:8000")
            return True
        else:
            print(f"❌ API недоступен, статус: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к API: {e}")
        return False

def check_database_connection():
    """Проверяет подключение к базе данных"""
    print("\n🔍 Проверка подключения к базе данных...")
    
    try:
        # Тестируем API endpoint который использует БД
        response = requests.get('http://5.129.198.80:8000/api/profile?tg_id=389694638', timeout=10)
        if response.status_code == 200:
            print("✅ База данных доступна")
            return True
        elif response.status_code == 404:
            print("✅ База данных доступна (профиль не найден - это нормально)")
            return True
        else:
            print(f"❌ Проблема с базой данных, статус: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False

def check_subscription_table():
    """Проверяет таблицу подписок"""
    print("\n🔍 Проверка таблицы подписок...")
    
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgresql+asyncpg://'):
            database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://', 1)
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Проверяем существование таблицы
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'subscriptions'
            );
        """)
        
        if cursor.fetchone()[0]:
            print("✅ Таблица subscriptions существует")
            
            # Проверяем структуру
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'subscriptions'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print(f"📋 Структура таблицы subscriptions:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
            
            # Проверяем количество записей
            cursor.execute("SELECT COUNT(*) FROM subscriptions;")
            count = cursor.fetchone()[0]
            print(f"📊 Количество записей: {count}")
            
        else:
            print("❌ Таблица subscriptions НЕ существует")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки таблицы подписок: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Проверка всех компонентов системы...")
    print("=" * 50)
    
    checks = [
        ("API URL", check_api_url),
        ("API Endpoints", check_api_endpoints),
        ("Платежная система", check_payment_system),
        ("Подключение к API", test_api_connection),
        ("База данных", check_database_connection),
        ("Таблица подписок", check_subscription_table)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Ошибка при проверке {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✅ ПРОЙДЕНА" if result else "❌ ПРОВАЛЕНА"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Система работает корректно.")
    else:
        print("⚠️  НЕКОТОРЫЕ ПРОВЕРКИ ПРОВАЛЕНЫ. Требуется исправление.")
        print("\n📋 РЕКОМЕНДАЦИИ:")
        print("1. Убедитесь что изменения загружены на сервер")
        print("2. Перезапустите контейнеры: docker-compose down && docker-compose up -d")
        print("3. Проверьте логи: docker-compose logs bot")
        print("4. Проверьте API: curl http://5.129.198.80:8000/health")

if __name__ == "__main__":
    main() 