#!/usr/bin/env python3
"""
Скрипт для исправления проблем со старым Docker
"""

import subprocess
import os
import sys
import requests
import time

def run_command(command):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_docker_version():
    """Проверяет версию Docker"""
    print("🔍 Проверка версии Docker...")
    
    success, output, error = run_command("docker --version")
    if success:
        print(f"📋 Версия Docker: {output.strip()}")
        return True
    else:
        print(f"❌ Ошибка проверки Docker: {error}")
        return False

def fix_requirements():
    """Исправляет requirements.txt для совместимости"""
    print("🔧 Исправление requirements.txt...")
    
    # Читаем текущий файл
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем проблемные зависимости
        replacements = [
            ('aiohttp~=3.9.0', 'aiohttp>=3.9.0,<3.12'),
            ('pydantic<2.11', 'pydantic>=2.0.0,<2.11'),
            ('aiofiles~=23.2.1', 'aiofiles>=23.0.0,<24.0.0'),
        ]
        
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                print(f"✅ Заменено: {old} → {new}")
        
        # Записываем исправленный файл
        with open('requirements.txt', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ requirements.txt исправлен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка исправления requirements.txt: {e}")
        return False

def stop_containers_old_docker():
    """Останавливает контейнеры для старого Docker"""
    print("🛑 Остановка контейнеров (старый Docker)...")
    
    commands = [
        "docker-compose down",
        "docker stop $(docker ps -q) 2>/dev/null || true",
        "docker system prune -f"  # Без compose для старого Docker
    ]
    
    for cmd in commands:
        print(f"Выполняю: {cmd}")
        success, output, error = run_command(cmd)
        if success:
            print(f"✅ Выполнено: {cmd}")
        else:
            print(f"⚠️  Команда не выполнена: {cmd}")
            if error:
                print(f"   Ошибка: {error}")

def clean_docker_old():
    """Очищает Docker для старого Docker"""
    print("🧹 Очистка Docker (старый Docker)...")
    
    commands = [
        "docker container prune -f",
        "docker image prune -f", 
        "docker volume prune -f",
        "docker network prune -f"
    ]
    
    for cmd in commands:
        success, output, error = run_command(cmd)
        if success:
            print(f"✅ Выполнено: {cmd}")
        else:
            print(f"⚠️  Команда не выполнена: {cmd}")

def rebuild_containers_old():
    """Пересобирает контейнеры для старого Docker"""
    print("🔨 Пересборка контейнеров (старый Docker)...")
    
    commands = [
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
            if output:
                print(f"   Вывод: {output}")
            return False
    
    return True

def wait_for_services():
    """Ждет запуска сервисов"""
    print("⏳ Ожидание запуска сервисов...")
    
    for i in range(60):  # Ждем максимум 60 секунд
        try:
            response = requests.get("http://5.129.198.80:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API запущен")
                break
        except:
            pass
        
        time.sleep(1)
        if i % 10 == 0:
            print(f"⏳ Ожидание... {i+1}/60")

def check_services_old():
    """Проверяет статус сервисов для старого Docker"""
    print("🔍 Проверка статуса сервисов...")
    
    success, output, error = run_command("docker-compose ps")
    if success:
        print("📋 Статус сервисов:")
        print(output)
        
        # Проверяем что все сервисы запущены
        if "Up" in output and "Exit" not in output:
            print("✅ Все сервисы запущены")
            return True
        else:
            print("⚠️  Не все сервисы запущены")
            return False
    else:
        print(f"❌ Ошибка проверки статуса: {error}")
        return False

def test_domains():
    """Тестирует домены"""
    print("🔍 Тестирование доменов...")
    
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

def check_logs():
    """Проверяет логи контейнеров"""
    print("📋 Проверка логов...")
    
    services = ["api", "bot", "frontend", "nginx"]
    
    for service in services:
        print(f"\n🔍 Логи {service}:")
        success, output, error = run_command(f"docker-compose logs --tail=10 {service}")
        if success:
            print(output)
        else:
            print(f"❌ Ошибка получения логов {service}: {error}")

def main():
    """Основная функция"""
    print("🚀 Исправление проблем со старым Docker...")
    print("=" * 60)
    
    # Проверяем версию Docker
    if not check_docker_version():
        print("❌ Docker не найден или не работает")
        return
    
    # Исправляем requirements.txt
    if not fix_requirements():
        print("❌ Не удалось исправить requirements.txt")
        return
    
    # Останавливаем контейнеры
    stop_containers_old_docker()
    
    # Очищаем Docker
    clean_docker_old()
    
    # Пересобираем и запускаем
    if rebuild_containers_old():
        # Ждем запуска сервисов
        wait_for_services()
        
        # Проверяем статус
        if check_services_old():
            # Проверяем логи
            check_logs()
            
            # Тестируем домены
            if test_domains():
                print("\n" + "=" * 60)
                print("🎉 ВСЕ ПРОБЛЕМЫ ИСПРАВЛЕНЫ!")
                print("=" * 60)
                print("📋 Доступные сервисы:")
                print("🌐 API: http://5.129.198.80:8000")
                print("📱 Frontend: https://твой-калькулятор.рф")
                print("📱 Frontend: https://tvoi-kalkulyator.ru")
                print("🤖 Бот: работает в контейнере")
                print("\n✅ Все сервисы работают корректно!")
            else:
                print("\n⚠️  Домены все еще не работают")
                print("Проверьте SSL сертификаты и DNS настройки")
        else:
            print("\n❌ Не все сервисы запущены")
            print("Проверьте логи: docker-compose logs")
    else:
        print("\n❌ ОШИБКА ПРИ ЗАПУСКЕ КОНТЕЙНЕРОВ!")
        print("Проверьте логи: docker-compose logs")

if __name__ == "__main__":
    main() 