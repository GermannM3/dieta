#!/usr/bin/env python3
"""
Экстренный скрипт для полной очистки и перезапуска всех сервисов
"""

import os
import subprocess
import time
import signal
import psutil
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_command(cmd, description=""):
    """Выполнить команду и вывести результат"""
    logging.info(f"🔄 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
        if result.stdout:
            logging.info(f"✅ {result.stdout.strip()}")
        if result.stderr:
            logging.warning(f"⚠️ {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        logging.error(f"❌ Ошибка выполнения команды '{cmd}': {e}")
        return False

def kill_process_on_port(port):
    """Убить процесс на порту"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                connections = proc.connections()
                for conn in connections:
                    if hasattr(conn, 'laddr') and conn.laddr.port == port:
                        logging.info(f"Убиваю процесс {proc.info['name']} (PID: {proc.info['pid']}) на порту {port}")
                        proc.terminate()
                        proc.wait(timeout=5)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        logging.error(f"Ошибка при поиске процессов на порту {port}: {e}")
    return False

def kill_all_processes():
    """Убить все процессы Python, npm, node и nginx"""
    logging.info("🔥 Убиваю все процессы...")

    # Остановить systemd сервисы
    run_command("sudo systemctl stop api frontend nginx bot", "Остановка systemd сервисов")

    # Убить процессы Python
    run_command("sudo pkill -f \"python.*main.py\"", "Убить процессы main.py")
    run_command("sudo pkill -f \"python.*main\"", "Убить процессы main")
    run_command("sudo pkill -f \"python.*improved_api_server\"", "Убить процессы API")
    run_command("sudo pkill -f \"python.*start_all_services\"", "Убить процессы start_all_services")

    # Убить процессы Node/NPM
    run_command("sudo pkill -f \"npm\"", "Убить процессы npm")
    run_command("sudo pkill -f \"vite\"", "Убить процессы vite")
    run_command("sudo pkill -f \"node\"", "Убить процессы node")

    # Убить процессы Nginx
    run_command("sudo pkill -f \"nginx\"", "Убить процессы nginx")

    # Принудительно освободить порты
    run_command("sudo lsof -ti :8000 | xargs sudo kill -9 2>/dev/null || true", "Освободить порт 8000")
    run_command("sudo lsof -ti :80 | xargs sudo kill -9 2>/dev/null || true", "Освободить порт 80")
    run_command("sudo lsof -ti :5173 | xargs sudo kill -9 2>/dev/null || true", "Освободить порт 5173")

    time.sleep(2) # Даем время процессам завершиться

    # Проверяем, остались ли процессы
    remaining_procs = subprocess.run("ps aux | grep -E \"(python|npm|node|nginx)\" | grep -v grep", shell=True, capture_output=True, text=True).stdout.strip()
    if remaining_procs:
        logging.warning(f"⚠️ Остались процессы: {remaining_procs}")
        return False
    else:
        logging.info("✅ Все процессы успешно убиты.")
        return True

def create_systemd_services():
    """Создать systemd unit файлы для бота и API"""
    logging.info("📝 Создаю systemd сервисы...")

    bot_service_content = """[Unit]
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
    api_service_content = """[Unit]
Description=Dieta API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/dieta
ExecStart=/opt/dieta/venv/bin/python -m uvicorn improved_api_server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    frontend_service_content = """[Unit]
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
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
"""
    nginx_config_content = """server {
    listen 80;
    server_name tvoi-kalkulyator.ru;

    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""

    run_command(f"echo \"{bot_service_content}\" | sudo tee /etc/systemd/system/bot.service > /dev/null", "Копирование bot.service")
    run_command(f"echo \"{api_service_content}\" | sudo tee /etc/systemd/system/api.service > /dev/null", "Копирование api.service")
    run_command(f"echo \"{frontend_service_content}\" | sudo tee /etc/systemd/system/frontend.service > /dev/null", "Копирование frontend.service")
    run_command(f"echo \"{nginx_config_content}\" | sudo tee /etc/nginx/sites-enabled/tvoi-kalkulyator > /dev/null", "Копирование Nginx конфига")

    # Удаляем дефолтный конфиг Nginx, если он есть
    run_command("sudo rm -f /etc/nginx/sites-enabled/default", "Удаление дефолтного конфига Nginx")

def start_services():
    """Запустить systemd сервисы"""
    logging.info("🚀 Запускаю сервисы...")
    run_command("sudo systemctl daemon-reload", "Перезагрузка systemd")
    run_command("sudo systemctl enable --now api", "Запуск API")
    run_command("sudo systemctl enable --now frontend", "Запуск Frontend")
    run_command("sudo systemctl enable --now nginx", "Запуск Nginx")
    run_command("sudo systemctl enable --now bot", "Запуск Bot")
    time.sleep(5) # Даем время сервисам запуститься

def check_status():
    """Проверить статус сервисов и процессов"""
    logging.info("🔍 Проверяю статус сервисов...")
    api_status = subprocess.run("sudo systemctl is-active api", shell=True, capture_output=True, text=True).stdout.strip()
    frontend_status = subprocess.run("sudo systemctl is-active frontend", shell=True, capture_output=True, text=True).stdout.strip()
    nginx_status = subprocess.run("sudo systemctl is-active nginx", shell=True, capture_output=True, text=True).stdout.strip()
    bot_status = subprocess.run("sudo systemctl is-active bot", shell=True, capture_output=True, text=True).stdout.strip()

    logging.info(f"✅ api: {api_status}")
    logging.info(f"✅ frontend: {frontend_status}")
    logging.info(f"✅ nginx: {nginx_status}")
    logging.info(f"✅ bot: {bot_status}")

    logging.info("🔍 Проверяю процессы...")
    bot_procs = subprocess.run("ps aux | grep 'main.py' | grep -v grep", shell=True, capture_output=True, text=True).stdout.strip()
    if bot_procs:
        logging.info(f"✅ Процессы бота: {bot_procs}")
    else:
        logging.warning("❌ Процессы бота не найдены.")

    logging.info("🔍 Проверяю порты...")
    port_8000 = subprocess.run("netstat -tlnp | grep 8000", shell=True, capture_output=True, text=True).stdout.strip()
    port_5173 = subprocess.run("netstat -tlnp | grep 5173", shell=True, capture_output=True, text=True).stdout.strip()
    port_80 = subprocess.run("netstat -tlnp | grep 80 ", shell=True, capture_output=True, text=True).stdout.strip()

    if port_8000:
        logging.info(f"✅ Порт 8000: {port_8000}")
    else:
        logging.warning("❌ Порт 8000: не используется")
    if port_5173:
        logging.info(f"✅ Порт 5173: {port_5173}")
    else:
        logging.warning("❌ Порт 5173: не используется")
    if port_80:
        logging.info(f"✅ Порт 80: {port_80}")
    else:
        logging.warning("❌ Порт 80: не используется")

    logging.info("🧪 Тестирую endpoints...")
    api_health_check = run_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/api/health", "API /api/health")
    frontend_check = run_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5173", "Frontend")
    nginx_check = run_command("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:80", "Nginx")

    if api_health_check:
        logging.info("✅ API /api/health работает")
    else:
        logging.error("❌ API /api/health не отвечает")
    if frontend_check:
        logging.info("✅ Frontend работает")
    else:
        logging.error("❌ Frontend не отвечает")
    if nginx_check:
        logging.info("✅ Nginx работает")
    else:
        logging.error("❌ Nginx не отвечает")

if __name__ == "__main__":
    print("🚨 ЭКСТРЕННЫЙ ПЕРЕЗАПУСК СЕРВИСОВ")
    print("==================================================")
    if kill_all_processes():
        create_systemd_services()
        start_services()
        check_status()
    else:
        logging.error("Не удалось убить все процессы. Пожалуйста, проверьте вручную и попробуйте снова.")

    print("\n🎯 ПРОВЕРКА БОТА:")
    print("1. Отправьте /start в Telegram")
    print("2. Проверьте что бот отвечает")
    print("3. Проверьте что команды работают")
    print("4. Проверьте что подписки работают")

    print("\n📊 МОНИТОРИНГ:")
    print("sudo journalctl -u bot -f")
    print("sudo journalctl -u api -f")
    print("sudo journalctl -u frontend -f") 