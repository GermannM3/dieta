#!/usr/bin/env python3
"""
Финальный фикс для исправления всех проблем с доменом и портами
"""

import subprocess
import os
import time
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def fix_all_issues():
    """Исправляем все проблемы"""
    logging.info("🔧 Финальное исправление всех проблем...")
    
    # 1. Останавливаем все старые процессы
    logging.info("🛑 Останавливаем старые процессы...")
    subprocess.run(["pkill", "-f", "npm start"], capture_output=True)
    subprocess.run(["pkill", "-f", "vite"], capture_output=True)
    time.sleep(3)
    
    # 2. Исправляем .env файлы
    logging.info("📝 Исправляем .env файлы...")
    
    # Основной .env
    main_env_path = "/opt/dieta/.env"
    if os.path.exists(main_env_path):
        with open(main_env_path, 'r') as f:
            content = f.read()
        
        # Заменяем IP на домен
        content = content.replace('http://5.129.198.80:8000', 'http://tvoi-kalkulyator.ru/api')
        content = content.replace('http://localhost:8000', 'http://tvoi-kalkulyator.ru/api')
        
        with open(main_env_path, 'w') as f:
            f.write(content)
        logging.info("✅ Основной .env исправлен")
    
    # Фронтенд .env
    frontend_env_path = "/opt/dieta/calorie-love-tracker/.env"
    frontend_env_content = """VITE_API_URL=http://tvoi-kalkulyator.ru/api
VITE_APP_TITLE=Твой Диетолог - Персональный ИИ-помощник
VITE_APP_DESCRIPTION=Продвинутый телеграм-бот с личным диетологом
VITE_TELEGRAM_BOT_USERNAME=@tvoy_diet_bot
PORT=3000"""
    
    with open(frontend_env_path, 'w') as f:
        f.write(frontend_env_content)
    logging.info("✅ Фронтенд .env исправлен")
    
    # 3. Устанавливаем systemd сервис
    logging.info("⚙️ Устанавливаем systemd сервис...")
    
    service_content = """[Unit]
Description=Dieta Frontend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/dieta/calorie-love-tracker
ExecStart=/usr/bin/npm start
Environment=PORT=3000
Environment=NODE_ENV=production
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target"""
    
    with open("/etc/systemd/system/frontend.service", 'w') as f:
        f.write(service_content)
    
    # Перезагружаем systemd и запускаем сервис
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "frontend"], check=True)
    subprocess.run(["systemctl", "start", "frontend"], check=True)
    
    logging.info("✅ Systemd сервис установлен и запущен")
    
    # 4. Ждем запуска
    logging.info("⏳ Ждем запуска фронтенда...")
    time.sleep(10)
    
    # 5. Проверяем статус
    result = subprocess.run(["systemctl", "is-active", "frontend"], 
                          capture_output=True, text=True)
    if result.stdout.strip() == "active":
        logging.info("✅ Фронтенд запущен через systemd")
        return True
    else:
        logging.error("❌ Фронтенд не запустился")
        return False

def test_services():
    """Тестируем все сервисы"""
    logging.info("🧪 Тестируем все сервисы...")
    
    import requests
    
    services = [
        ("API", "http://tvoi-kalkulyator.ru/api/health"),
        ("Сайт", "http://tvoi-kalkulyator.ru"),
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                logging.info(f"✅ {name} работает")
            else:
                logging.warning(f"⚠️ {name} вернул {response.status_code}")
        except Exception as e:
            logging.error(f"❌ {name} не отвечает: {e}")

def show_status():
    """Показываем статус сервисов"""
    logging.info("📊 Статус сервисов:")
    
    services = ["nginx", "frontend"]
    for service in services:
        result = subprocess.run(["systemctl", "is-active", service], 
                              capture_output=True, text=True)
        status = result.stdout.strip()
        if status == "active":
            logging.info(f"✅ {service}: активен")
        else:
            logging.warning(f"⚠️ {service}: {status}")

if __name__ == "__main__":
    if fix_all_issues():
        time.sleep(5)
        show_status()
        test_services()
        logging.info("🎉 Все исправления применены!")
        logging.info("🌐 Сайт: http://tvoi-kalkulyator.ru")
        logging.info("🔗 API: http://tvoi-kalkulyator.ru/api/health")
    else:
        logging.error("❌ Не удалось применить исправления") 