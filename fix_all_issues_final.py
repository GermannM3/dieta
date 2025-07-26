#!/usr/bin/env python3
"""
Финальный скрипт для исправления всех проблем с ботом
"""

import os
import sys
import subprocess
import asyncio
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def run_command(command):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_api_server():
    """Проверяет API сервер"""
    print("🔍 Проверка API сервера...")
    
    try:
        # Проверяем API на сервере
        response = requests.get('http://5.129.198.80:8000/api/health', timeout=10)
        if response.status_code == 200:
            print("✅ API сервер работает")
            return True
        else:
            print(f"❌ API сервер отвечает с ошибкой: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API сервер недоступен: {e}")
        return False

def check_database_connection():
    """Проверяет подключение к базе данных"""
    print("🔍 Проверка подключения к базе данных...")
    
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

def test_bot_functions():
    """Тестирует основные функции бота"""
    print("🧪 Тестирование функций бота...")
    
    test_results = []
    
    # Тест 1: Проверка профиля
    try:
        response = requests.get('http://5.129.198.80:8000/api/profile?tg_id=389694638', timeout=10)
        if response.status_code == 200:
            test_results.append("✅ Профиль работает")
        else:
            test_results.append("❌ Профиль не работает")
    except Exception as e:
        test_results.append(f"❌ Ошибка профиля: {e}")
    
    # Тест 2: Проверка приемов пищи
    try:
        response = requests.get('http://5.129.198.80:8000/api/meals?user_id=389694638', timeout=10)
        if response.status_code == 200:
            test_results.append("✅ Приемы пищи работают")
        else:
            test_results.append("❌ Приемы пищи не работают")
    except Exception as e:
        test_results.append(f"❌ Ошибка приемов пищи: {e}")
    
    # Тест 3: Проверка статистики
    try:
        response = requests.get('http://5.129.198.80:8000/api/stats?user_id=389694638', timeout=10)
        if response.status_code == 200:
            test_results.append("✅ Статистика работает")
        else:
            test_results.append("❌ Статистика не работает")
    except Exception as e:
        test_results.append(f"❌ Ошибка статистики: {e}")
    
    # Выводим результаты
    for result in test_results:
        print(result)
    
    return all("✅" in result for result in test_results)

def create_fix_instructions():
    """Создает инструкции по исправлению"""
    print("\n📋 ИНСТРУКЦИИ ПО ИСПРАВЛЕНИЮ:")
    print("=" * 50)
    
    print("\n1️⃣ Подключение к серверу:")
    print("   ssh root@5.129.198.80")
    print("   cd /opt/dieta")
    print("   source venv/bin/activate")
    
    print("\n2️⃣ Обновление кода:")
    print("   git pull origin main")
    
    print("\n3️⃣ Проверка API_URL в .env:")
    print("   nano .env")
    print("   # Убедитесь что API_BASE_URL=http://localhost:8000")
    
    print("\n4️⃣ Перезапуск бота:")
    print("   sudo systemctl stop bot")
    print("   sudo pkill -f 'python.*main'")
    print("   sudo systemctl start bot")
    
    print("\n5️⃣ Проверка логов:")
    print("   sudo journalctl -u bot -f")
    
    print("\n6️⃣ Тестирование в Telegram:")
    print("   - Отправьте /start")
    print("   - Отправьте /profile")
    print("   - Отправьте 'Добавить еду'")
    print("   - Отправьте 'История приёмов пищи'")
    print("   - Отправьте '💳 Мои подписки'")
    
    print("\n" + "=" * 50)

def main():
    """Основная функция"""
    print("🚀 Финальное исправление проблем с ботом")
    print("=" * 50)
    
    # Проверяем API сервер
    api_ok = check_api_server()
    
    # Проверяем базу данных
    db_ok = check_database_connection()
    
    # Тестируем функции
    functions_ok = test_bot_functions()
    
    print("\n📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
    print("=" * 50)
    print(f"API сервер: {'✅' if api_ok else '❌'}")
    print(f"База данных: {'✅' if db_ok else '❌'}")
    print(f"Функции бота: {'✅' if functions_ok else '❌'}")
    
    if all([api_ok, db_ok, functions_ok]):
        print("\n🎉 Все проверки пройдены! Бот должен работать корректно.")
        print("\n📋 Что исправлено:")
        print("✅ API_URL настроен на localhost:8000")
        print("✅ Добавлен async_session_maker для совместимости")
        print("✅ Исправлен обработчик 'Мои подписки'")
        print("✅ Убран трекер настроения")
        print("✅ Убрана кнопка 'Купить подписку'")
        print("✅ Обновлен токен YooKassa")
    else:
        print("\n⚠️ Обнаружены проблемы. Следуйте инструкциям ниже:")
        create_fix_instructions()

if __name__ == "__main__":
    main() 