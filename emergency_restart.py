#!/usr/bin/env python3
"""
Экстренный скрипт для полной очистки и перезапуска всех сервисов
"""

import os
import subprocess
import time
import signal
import psutil

def run_command(cmd, description=""):
    """Выполнить команду и вывести результат"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout}")
        if result.stderr:
            print(f"⚠️ {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def kill_all_processes():
    """Убить все процессы Python и npm"""
    print("🔥 Убиваю все процессы...")
    
    # Остановить systemd сервисы
    run_command("sudo systemctl stop api frontend nginx bot", "Остановка systemd сервисов")
    
    # Убить все процессы Python
    run_command("sudo pkill -f 'python.*main.py'", "Убить процессы main.py")
    run_command("sudo pkill -f 'python.*main'", "Убить процессы main")
    run_command("sudo pkill -f 'python.*improved_api_server'", "Убить процессы API")
    run_command("sudo pkill -f 'python.*start_all_services'", "Убить процессы start_all_services")
    
    # Убить npm процессы
    run_command("sudo pkill -f 'npm'", "Убить процессы npm")
    run_command("sudo pkill -f 'vite'", "Убить процессы vite")
    run_command("sudo pkill -f 'node'", "Убить процессы node")
    
    # Принудительно освободить порты
    run_command("sudo lsof -ti :8000 | xargs sudo kill -9 2>/dev/null || true", "Освободить порт 8000")
    run_command("sudo lsof -ti :80 | xargs sudo kill -9 2>/dev/null || true", "Освободить порт 80")
    run_command("sudo lsof -ti :5173 | xargs sudo kill -9 2>/dev/null || true", "Освободить порт 5173")
    
    time.sleep(3)
    
    # Проверить что все убиты
    result = subprocess.run("ps aux | grep -E '(python|npm)' | grep -v grep", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print(f"⚠️ Остались процессы: {result.stdout}")
        return False
    else:
        print("✅ Все процессы убиты")
        return True

def create_systemd_services():
    """Создать systemd сервисы"""
    print("📝 Создаю systemd сервисы...")
    
    # Создать bot.service
    bot_service = """[Unit]
Description=Dieta Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/dieta
ExecStart=/opt/dieta/venv/bin/python main.py
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    
    with open("/tmp/bot.service", "w") as f:
        f.write(bot_service)
    
    run_command("sudo cp /tmp/bot.service /etc/systemd/system/", "Копирование bot.service")
    
    # Создать api.service если не существует
    if not os.path.exists("/etc/systemd/system/api.service"):
        api_service = """[Unit]
Description=Dieta API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/dieta
ExecStart=/opt/dieta/venv/bin/python -m uvicorn improved_api_server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        
        with open("/tmp/api.service", "w") as f:
            f.write(api_service)
        
        run_command("sudo cp /tmp/api.service /etc/systemd/system/", "Копирование api.service")
    
    # Создать frontend.service если не существует
    if not os.path.exists("/etc/systemd/system/frontend.service"):
        frontend_service = """[Unit]
Description=Dieta Frontend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/dieta/calorie-love-tracker
ExecStart=/usr/bin/npm start
Environment=PORT=5173
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""
        
        with open("/tmp/frontend.service", "w") as f:
            f.write(frontend_service)
        
        run_command("sudo cp /tmp/frontend.service /etc/systemd/system/", "Копирование frontend.service")

def start_services():
    """Запустить все сервисы"""
    print("🚀 Запускаю сервисы...")
    
    # Перезагрузить systemd
    run_command("sudo systemctl daemon-reload", "Перезагрузка systemd")
    
    # Запустить сервисы
    run_command("sudo systemctl enable --now api", "Запуск API")
    time.sleep(2)
    
    run_command("sudo systemctl enable --now frontend", "Запуск Frontend")
    time.sleep(2)
    
    run_command("sudo systemctl enable --now nginx", "Запуск Nginx")
    time.sleep(2)
    
    run_command("sudo systemctl enable --now bot", "Запуск Bot")
    time.sleep(3)

def check_services():
    """Проверить статус сервисов"""
    print("🔍 Проверяю статус сервисов...")
    
    services = ["api", "frontend", "nginx", "bot"]
    for service in services:
        result = subprocess.run(f"sudo systemctl is-active {service}", shell=True, capture_output=True, text=True)
        status = result.stdout.strip()
        if status == "active":
            print(f"✅ {service}: {status}")
        else:
            print(f"❌ {service}: {status}")
    
    # Проверить процессы
    print("\n🔍 Проверяю процессы...")
    result = subprocess.run("ps aux | grep 'main.py' | grep -v grep", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print(f"✅ Процессы бота: {result.stdout}")
    else:
        print("❌ Процессы бота не найдены")
    
    # Проверить порты
    print("\n🔍 Проверяю порты...")
    ports = [8000, 5173, 80]
    for port in ports:
        result = subprocess.run(f"netstat -tlnp | grep :{port}", shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ Порт {port}: {result.stdout.strip()}")
        else:
            print(f"❌ Порт {port}: не используется")

def test_endpoints():
    """Тестировать endpoints"""
    print("🧪 Тестирую endpoints...")
    
    # Тест API
    result = subprocess.run("curl -s http://localhost:8000/api/health", shell=True, capture_output=True, text=True)
    if result.stdout and "healthy" in result.stdout:
        print("✅ API /api/health работает")
    else:
        print("❌ API /api/health не отвечает")
    
    # Тест Frontend
    result = subprocess.run("curl -s -I http://localhost:5173", shell=True, capture_output=True, text=True)
    if "200 OK" in result.stdout:
        print("✅ Frontend работает")
    else:
        print("❌ Frontend не отвечает")
    
    # Тест Nginx
    result = subprocess.run("curl -s -I http://localhost", shell=True, capture_output=True, text=True)
    if "200 OK" in result.stdout:
        print("✅ Nginx работает")
    else:
        print("❌ Nginx не отвечает")

def main():
    """Главная функция"""
    print("🚨 ЭКСТРЕННЫЙ ПЕРЕЗАПУСК СЕРВИСОВ")
    print("=" * 50)
    
    # Проверить что мы в правильной директории
    if not os.path.exists("main.py"):
        print("❌ Файл main.py не найден. Перейдите в директорию /opt/dieta")
        return
    
    # 1. Убить все процессы
    if not kill_all_processes():
        print("⚠️ Не все процессы были убиты")
    
    # 2. Создать systemd сервисы
    create_systemd_services()
    
    # 3. Запустить сервисы
    start_services()
    
    # 4. Проверить статус
    check_services()
    
    # 5. Тестировать endpoints
    test_endpoints()
    
    print("\n🎯 ПРОВЕРКА БОТА:")
    print("1. Отправьте /start в Telegram")
    print("2. Проверьте что бот отвечает")
    print("3. Проверьте что команды работают")
    print("4. Проверьте что подписки работают")
    
    print("\n📊 МОНИТОРИНГ:")
    print("sudo journalctl -u bot -f")
    print("sudo journalctl -u api -f")
    print("sudo journalctl -u frontend -f")

if __name__ == "__main__":
    main() 