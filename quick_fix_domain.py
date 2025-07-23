#!/usr/bin/env python3
"""
Быстрый фикс для исправления домена на сервере
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

def fix_domain_issues():
    """Исправляем проблемы с доменом"""
    logging.info("🔧 Исправляем проблемы с доменом...")
    
    # 1. Останавливаем старые процессы фронтенда
    logging.info("🛑 Останавливаем старые процессы фронтенда...")
    subprocess.run(["pkill", "-f", "npm start"], capture_output=True)
    subprocess.run(["pkill", "-f", "vite"], capture_output=True)
    time.sleep(2)
    
    # 2. Создаем правильный .env файл
    logging.info("📝 Создаем правильный .env файл...")
    env_content = """VITE_API_URL=http://tvoi-kalkulyator.ru/api
VITE_APP_TITLE=Твой Диетолог - Персональный ИИ-помощник
VITE_APP_DESCRIPTION=Продвинутый телеграм-бот с личным диетологом
VITE_TELEGRAM_BOT_USERNAME=@tvoy_diet_bot
PORT=3000"""
    
    with open("calorie-love-tracker/.env", "w") as f:
        f.write(env_content)
    
    # 3. Запускаем фронтенд на правильном порту
    logging.info("🚀 Запускаем фронтенд на порту 3000...")
    frontend_dir = "calorie-love-tracker"
    
    # Устанавливаем переменную окружения
    env = os.environ.copy()
    env["PORT"] = "3000"
    
    process = subprocess.Popen(
        ["npm", "start"],
        cwd=frontend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Ждем запуска
    time.sleep(10)
    
    if process.poll() is None:
        logging.info("✅ Фронтенд запущен на порту 3000")
        logging.info("🌐 Сайт: http://tvoi-kalkulyator.ru")
        logging.info("🔗 API: http://tvoi-kalkulyator.ru/api/health")
        return True
    else:
        stdout, stderr = process.communicate()
        logging.error(f"❌ Ошибка запуска фронтенда: {stderr}")
        return False

def test_services():
    """Тестируем сервисы"""
    logging.info("🧪 Тестируем сервисы...")
    
    import requests
    
    # Тест API
    try:
        response = requests.get("http://tvoi-kalkulyator.ru/api/health", timeout=5)
        if response.status_code == 200:
            logging.info("✅ API работает")
        else:
            logging.error(f"❌ API вернул {response.status_code}")
    except Exception as e:
        logging.error(f"❌ API не отвечает: {e}")
    
    # Тест сайта
    try:
        response = requests.get("http://tvoi-kalkulyator.ru", timeout=5)
        if response.status_code == 200:
            logging.info("✅ Сайт работает")
        else:
            logging.error(f"❌ Сайт вернул {response.status_code}")
    except Exception as e:
        logging.error(f"❌ Сайт не отвечает: {e}")

if __name__ == "__main__":
    if fix_domain_issues():
        time.sleep(5)
        test_services()
    else:
        logging.error("❌ Не удалось исправить проблемы") 