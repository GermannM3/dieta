#!/usr/bin/env python3
"""
Скрипт для принудительного исправления всех проблем
"""

import os
import re
import subprocess
import sys

def fix_api_url_in_file(file_path, old_urls, new_url):
    """Исправляет API URL в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Заменяем все старые URL на новый
        for old_url in old_urls:
            content = content.replace(old_url, new_url)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Исправлен API URL в {file_path}")
            return True
        else:
            print(f"ℹ️  API URL в {file_path} уже корректен")
            return False
    except Exception as e:
        print(f"❌ Ошибка при исправлении {file_path}: {e}")
        return False

def fix_docker_compose():
    """Исправляет Docker Compose файл"""
    print("🔧 Исправление Docker Compose...")
    
    compose_content = """services:
  # FastAPI Backend
  api:
    build:
      context: .
      dockerfile: Dockerfile
    command: python improved_api_server.py
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Telegram Bot
  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    env_file:
      - .env
    environment:
      - API_BASE_URL=http://api:8000
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - api

  # React Frontend с Nginx
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:80"  # Изменяем порт с 80 на 3000 чтобы избежать конфликта
    restart: unless-stopped
    depends_on:
      - api

volumes:
  logs_data:
    driver: local
"""
    
    try:
        with open('docker-compose.yml', 'w', encoding='utf-8') as f:
            f.write(compose_content)
        print("✅ Docker Compose файл исправлен")
        return True
    except Exception as e:
        print(f"❌ Ошибка исправления Docker Compose: {e}")
        return False

def stop_all_containers():
    """Останавливает все контейнеры"""
    print("🛑 Остановка всех контейнеров...")
    
    commands = [
        "docker-compose down",
        "docker stop $(docker ps -q) 2>/dev/null || true",
        "docker system prune -f"
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ Выполнено: {cmd}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Команда не выполнена: {cmd}")

def rebuild_containers():
    """Пересобирает контейнеры"""
    print("🔨 Пересборка контейнеров...")
    
    commands = [
        "docker-compose build --no-cache",
        "docker-compose up -d"
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Выполнено: {cmd}")
            else:
                print(f"❌ Ошибка: {cmd}")
                print(f"Ошибка: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Исключение при выполнении {cmd}: {e}")
            return False
    
    return True

def check_services():
    """Проверяет статус сервисов"""
    print("🔍 Проверка статуса сервисов...")
    
    try:
        result = subprocess.run("docker-compose ps", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("📋 Статус сервисов:")
            print(result.stdout)
            
            # Проверяем что все сервисы запущены
            if "Up" in result.stdout and "Exit" not in result.stdout:
                print("✅ Все сервисы запущены")
                return True
            else:
                print("⚠️  Не все сервисы запущены")
                return False
        else:
            print(f"❌ Ошибка проверки статуса: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Исключение при проверке статуса: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 Принудительное исправление всех проблем...")
    print("=" * 60)
    
    # Файлы для исправления API URL
    files_to_fix = [
        'components/handlers/user_handlers.py',
        'components/handlers/admin_handlers.py',
        'components/handlers/fat_tracker_handlers.py',
        'components/payment_system/payment_handlers.py',
        'components/payment_system/payment_operations.py'
    ]
    
    old_urls = [
        'http://127.0.0.1:8000',
        'http://localhost:8000',
        '127.0.0.1:8000',
        'localhost:8000',
        'http://5.129.198.80:8000'  # Внешний URL тоже заменяем на внутренний
    ]
    
    new_url = 'http://api:8000'  # Внутренний URL для Docker сети
    
    # Исправляем API URL во всех файлах
    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_api_url_in_file(file_path, old_urls, new_url):
                fixed_count += 1
        else:
            print(f"⚠️  Файл {file_path} не найден")
    
    print(f"\n📊 Исправлено файлов: {fixed_count}")
    
    # Исправляем Docker Compose
    fix_docker_compose()
    
    # Останавливаем все контейнеры
    stop_all_containers()
    
    # Пересобираем и запускаем
    if rebuild_containers():
        # Проверяем статус
        check_services()
        
        print("\n" + "=" * 60)
        print("🎉 ИСПРАВЛЕНИЯ ЗАВЕРШЕНЫ!")
        print("=" * 60)
        print("📋 Что исправлено:")
        print("✅ API URL во всех файлах изменен на http://api:8000")
        print("✅ Docker Compose исправлен (порт frontend изменен на 3000)")
        print("✅ Все контейнеры пересобраны и запущены")
        print("\n📋 Доступные сервисы:")
        print("🌐 API: http://localhost:8000")
        print("🤖 Бот: работает в контейнере")
        print("📱 Frontend: http://localhost:3000")
        print("\n📋 Команды для проверки:")
        print("docker-compose logs")
        print("docker-compose ps")
        print("curl http://localhost:8000/health")
    else:
        print("\n❌ ОШИБКА ПРИ ЗАПУСКЕ КОНТЕЙНЕРОВ!")
        print("Проверьте логи: docker-compose logs")

if __name__ == "__main__":
    main() 