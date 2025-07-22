#!/usr/bin/env python3
"""
Скрипт для проверки статуса сервера 5.129.198.80
"""

import subprocess
import requests
import sys
import os

def run_command(command):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_docker_containers():
    """Проверяет статус Docker контейнеров"""
    print("🔍 Проверка Docker контейнеров...")
    
    success, output, error = run_command("docker-compose ps")
    if success:
        print("📋 Статус контейнеров:")
        print(output)
        
        # Проверяем что все сервисы запущены
        if "Up" in output and "Exit" not in output:
            print("✅ Все контейнеры запущены")
            return True
        else:
            print("⚠️  Не все контейнеры запущены")
            return False
    else:
        print(f"❌ Ошибка проверки контейнеров: {error}")
        return False

def check_api_health():
    """Проверяет здоровье API"""
    print("\n🔍 Проверка API (5.129.198.80:8000)...")
    
    try:
        response = requests.get("http://5.129.198.80:8000/health", timeout=10)
        if response.status_code == 200:
            print("✅ API работает корректно")
            return True
        else:
            print(f"⚠️  API вернул статус: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к API: {e}")
        return False

def check_frontend_domains():
    """Проверяет доступность фронтенда по доменам"""
    print("\n🔍 Проверка фронтенда по доменам...")
    
    domains = [
        "https://твой-калькулятор.рф",
        "https://tvoi-kalkulyator.ru"
    ]
    
    all_working = True
    for domain in domains:
        try:
            response = requests.get(domain, timeout=10, verify=False)
            if response.status_code == 200:
                print(f"✅ {domain} - работает")
            else:
                print(f"⚠️  {domain} - статус {response.status_code}")
                all_working = False
        except requests.exceptions.RequestException as e:
            print(f"❌ {domain} - ошибка: {e}")
            all_working = False
    
    return all_working

def check_frontend_port():
    """Проверяет фронтенд на порту 3000"""
    print("\n🔍 Проверка фронтенда (5.129.198.80:3000)...")
    
    try:
        response = requests.get("http://5.129.198.80:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend на порту 3000 работает")
            return True
        else:
            print(f"⚠️  Frontend вернул статус: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения к frontend: {e}")
        return False

def check_bot_logs():
    """Проверяет логи бота"""
    print("\n🔍 Проверка логов бота...")
    
    success, output, error = run_command("docker-compose logs --tail=20 bot")
    if success:
        print("📋 Последние логи бота:")
        print(output)
        
        # Проверяем на ошибки
        if "ERROR" in output or "Exception" in output:
            print("⚠️  Обнаружены ошибки в логах бота")
            return False
        else:
            print("✅ Логи бота без ошибок")
            return True
    else:
        print(f"❌ Ошибка получения логов: {error}")
        return False

def check_api_logs():
    """Проверяет логи API"""
    print("\n🔍 Проверка логов API...")
    
    success, output, error = run_command("docker-compose logs --tail=20 api")
    if success:
        print("📋 Последние логи API:")
        print(output)
        
        # Проверяем на ошибки
        if "ERROR" in output or "Exception" in output:
            print("⚠️  Обнаружены ошибки в логах API")
            return False
        else:
            print("✅ Логи API без ошибок")
            return True
    else:
        print(f"❌ Ошибка получения логов: {error}")
        return False

def rebuild_containers():
    """Пересобирает контейнеры"""
    print("\n🔨 Пересборка контейнеров...")
    
    commands = [
        "docker-compose down",
        "docker-compose build --no-cache",
        "docker-compose up -d"
    ]
    
    for cmd in commands:
        print(f"Выполняю: {cmd}")
        success, output, error = run_command(cmd)
        if success:
            print(f"✅ {cmd} - выполнено")
        else:
            print(f"❌ {cmd} - ошибка: {error}")
            return False
    
    return True

def main():
    """Основная функция"""
    print("🚀 Проверка статуса сервера 5.129.198.80")
    print("=" * 60)
    
    checks = [
        ("Docker контейнеры", check_docker_containers),
        ("API здоровье", check_api_health),
        ("Frontend домены", check_frontend_domains),
        ("Frontend порт 3000", check_frontend_port),
        ("Логи бота", check_bot_logs),
        ("Логи API", check_api_logs)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Ошибка при проверке {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ РАБОТАЕТ" if result else "❌ НЕ РАБОТАЕТ"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ВСЕ СЕРВИСЫ РАБОТАЮТ КОРРЕКТНО!")
        print("\n📋 Доступные сервисы:")
        print("🌐 API: http://5.129.198.80:8000")
        print("📱 Frontend: https://твой-калькулятор.рф")
        print("📱 Frontend: https://tvoi-kalkulyator.ru")
        print("🤖 Бот: работает в контейнере")
    else:
        print("⚠️  НЕКОТОРЫЕ СЕРВИСЫ НЕ РАБОТАЮТ")
        print("\n🔧 РЕКОМЕНДАЦИИ:")
        print("1. Пересоберите контейнеры: python check_server_status.py --rebuild")
        print("2. Проверьте логи: docker-compose logs")
        print("3. Проверьте порты: netstat -tlnp | grep :80")
    
    # Если передан флаг --rebuild, пересобираем контейнеры
    if "--rebuild" in sys.argv:
        print("\n🔨 Запуск пересборки контейнеров...")
        if rebuild_containers():
            print("✅ Пересборка завершена")
            print("Повторите проверку: python check_server_status.py")
        else:
            print("❌ Ошибка при пересборке")

if __name__ == "__main__":
    main() 