#!/usr/bin/env python3
"""
Скрипт для исправления всех проблем на сервере
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

def fix_nginx_config():
    """Исправляет nginx конфигурацию"""
    print("🔧 Исправление nginx конфигурации...")
    
    nginx_config = """server {
    listen 80;
    listen 443 ssl;
    server_name твой-калькулятор.рф tvoi-kalkulyator.ru www.твой-калькулятор.рф www.tvoi-kalkulyator.ru;
    
    # SSL конфигурация
    ssl_certificate /etc/ssl/certs/ssl-cert.pem;
    ssl_certificate_key /etc/ssl/private/ssl-cert.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    root /usr/share/nginx/html;
    index index.html;
    
    # Обработка React Router
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Проксирование API запросов
    location /api {
        proxy_pass http://api:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Кэширование статических файлов
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml application/json;
    gzip_disable "MSIE [1-6]\\.";
}"""
    
    try:
        with open('nginx.conf', 'w', encoding='utf-8') as f:
            f.write(nginx_config)
        print("✅ nginx конфигурация исправлена")
        return True
    except Exception as e:
        print(f"❌ Ошибка исправления nginx: {e}")
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

  # Nginx для доменов
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/ssl
    restart: unless-stopped
    depends_on:
      - frontend
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
        success, output, error = run_command(cmd)
        if success:
            print(f"✅ Выполнено: {cmd}")
        else:
            print(f"⚠️  Команда не выполнена: {cmd}")

def rebuild_containers():
    """Пересобирает контейнеры"""
    print("🔨 Пересборка контейнеров...")
    
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
            return False
    
    return True

def wait_for_services():
    """Ждет запуска сервисов"""
    print("⏳ Ожидание запуска сервисов...")
    
    for i in range(30):  # Ждем максимум 30 секунд
        try:
            response = requests.get("http://5.129.198.80:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API запущен")
                break
        except:
            pass
        
        time.sleep(1)
        if i % 5 == 0:
            print(f"⏳ Ожидание... {i+1}/30")

def check_services():
    """Проверяет статус сервисов"""
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

def main():
    """Основная функция"""
    print("🚀 Исправление всех проблем на сервере...")
    print("=" * 60)
    
    # Исправляем конфигурации
    fix_nginx_config()
    fix_docker_compose()
    
    # Останавливаем все контейнеры
    stop_all_containers()
    
    # Пересобираем и запускаем
    if rebuild_containers():
        # Ждем запуска сервисов
        wait_for_services()
        
        # Проверяем статус
        if check_services():
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