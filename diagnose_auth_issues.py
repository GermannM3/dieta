#!/usr/bin/env python3
"""
Скрипт для диагностики проблем с аутентификацией и базой данных
"""

import requests
import json
import sys
from datetime import datetime

def test_api_health():
    """Тестирует доступность API"""
    print("🔍 Тестирование API...")
    
    try:
        response = requests.get("http://5.129.198.80:8000/health", timeout=10)
        print(f"✅ API доступен: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"📊 Статус API: {data}")
        return True
    except Exception as e:
        print(f"❌ API недоступен: {e}")
        return False

def test_auth_endpoints():
    """Тестирует эндпоинты аутентификации"""
    print("\n🔐 Тестирование эндпоинтов аутентификации...")
    
    base_url = "http://5.129.198.80:8000"
    
    # Тест регистрации
    try:
        test_user = {
            "email": "test@example.com",
            "password": "test123456",
            "name": "Test User"
        }
        
        response = requests.post(f"{base_url}/auth/register", json=test_user, timeout=10)
        print(f"📝 Регистрация: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Регистрация успешна: {data.get('user', {}).get('email')}")
            return data.get('access_token')
        elif response.status_code == 400:
            data = response.json()
            print(f"⚠️ Ошибка регистрации: {data.get('detail')}")
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования регистрации: {e}")
    
    # Тест входа
    try:
        login_data = {
            "email": "test@example.com",
            "password": "test123456"
        }
        
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=10)
        print(f"🔑 Вход: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Вход успешен: {data.get('user', {}).get('email')}")
            return data.get('access_token')
        elif response.status_code == 401:
            print("❌ Неверные учетные данные")
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования входа: {e}")
    
    return None

def test_admin_login():
    """Тестирует вход под админом"""
    print("\n👑 Тестирование входа под админом...")
    
    try:
        admin_data = {
            "email": "germannm@vk.com",
            "password": "Germ@nnM3"
        }
        
        response = requests.post("http://5.129.198.80:8000/auth/login", json=admin_data, timeout=10)
        print(f"🔑 Вход админа: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Вход админа успешен!")
            print(f"📧 Email: {data.get('user', {}).get('email')}")
            print(f"🆔 User ID: {data.get('user', {}).get('id')}")
            return data.get('access_token')
        elif response.status_code == 401:
            print("❌ Неверные учетные данные админа")
            data = response.json()
            print(f"📝 Детали: {data.get('detail')}")
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            data = response.json()
            print(f"📝 Ответ: {data}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования входа админа: {e}")
    
    return None

def test_database_connection():
    """Тестирует подключение к базе данных"""
    print("\n🗄️ Тестирование подключения к базе данных...")
    
    try:
        # Тестируем через API
        response = requests.get("http://5.129.198.80:8000/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'database' in data:
                print(f"✅ База данных: {data['database']}")
            else:
                print("⚠️ Информация о БД не найдена в ответе")
        else:
            print(f"❌ API недоступен: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования БД: {e}")

def test_frontend_connection():
    """Тестирует доступность фронтенда"""
    print("\n🌐 Тестирование фронтенда...")
    
    urls = [
        "http://5.129.198.80:3000",
        "http://tvoi-kalkulyator.ru",
        "http://твой-калькулятор.рф"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {url}: {response.status_code}")
        except Exception as e:
            print(f"❌ {url}: {e}")

def main():
    """Основная функция диагностики"""
    print("🔧 Диагностика проблем с аутентификацией и доменами")
    print("=" * 60)
    print(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Тестируем API
    api_ok = test_api_health()
    
    if api_ok:
        # Тестируем аутентификацию
        token = test_auth_endpoints()
        
        # Тестируем вход админа
        admin_token = test_admin_login()
        
        # Тестируем базу данных
        test_database_connection()
    else:
        print("❌ API недоступен, пропускаем тесты аутентификации")
    
    # Тестируем фронтенд
    test_frontend_connection()
    
    print("\n" + "=" * 60)
    print("📋 Рекомендации:")
    
    if not api_ok:
        print("1. 🔧 Проверьте, что API сервер запущен: sudo systemctl status api")
        print("2. 🔧 Проверьте логи API: sudo journalctl -u api -f")
    
    print("3. 🌐 Проверьте DNS настройки доменов")
    print("4. 🔧 Проверьте nginx: sudo nginx -t && sudo systemctl status nginx")
    print("5. 🔧 Проверьте фронтенд: sudo systemctl status frontend")

if __name__ == "__main__":
    main() 