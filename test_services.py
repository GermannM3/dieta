#!/usr/bin/env python3
"""
Скрипт для ручного тестирования сервисов
"""

import subprocess
import sys
import os
import time
import asyncio
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_database():
    """Тест подключения к базе данных"""
    logging.info("🗄️ Тестируем подключение к базе данных...")
    
    try:
        # Импортируем необходимые модули
        from database.init_database import engine
        from sqlalchemy import text
        
        # Пробуем подключиться
        with engine.begin() as conn:
            result = conn.execute(text("SELECT 1"))
            logging.info("✅ База данных работает")
            return True
    except Exception as e:
        logging.error(f"❌ Ошибка базы данных: {e}")
        return False

def test_api():
    """Тест API сервера"""
    logging.info("🚀 Тестируем API сервер...")
    
    try:
        # Запускаем API сервер
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "improved_api_server:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем запуска
        time.sleep(5)
        
        if process.poll() is None:
            logging.info("✅ API сервер запущен")
            
            # Проверяем health endpoint
            try:
                import requests
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    logging.info("✅ API health endpoint работает")
                    process.terminate()
                    return True
                else:
                    logging.error(f"❌ API health endpoint вернул {response.status_code}")
                    process.terminate()
                    return False
            except Exception as e:
                logging.error(f"❌ Не удалось проверить API: {e}")
                process.terminate()
                return False
        else:
            stdout, stderr = process.communicate()
            logging.error(f"❌ API сервер не запустился: {stderr}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Ошибка запуска API: {e}")
        return False

def test_bot():
    """Тест бота"""
    logging.info("🤖 Тестируем бота...")
    
    try:
        # Запускаем бота
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем запуска
        time.sleep(5)
        
        if process.poll() is None:
            logging.info("✅ Бот запущен")
            process.terminate()
            return True
        else:
            stdout, stderr = process.communicate()
            logging.error(f"❌ Бот не запустился: {stderr}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Ошибка запуска бота: {e}")
        return False

def test_frontend():
    """Тест фронтенда"""
    logging.info("🌐 Тестируем фронтенд...")
    
    frontend_dir = "calorie-love-tracker"
    if not os.path.exists(frontend_dir):
        logging.error(f"❌ Директория {frontend_dir} не найдена")
        return False
    
    try:
        # Проверяем node_modules
        if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
            logging.info("📦 Устанавливаем зависимости фронтенда...")
            install_process = subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                capture_output=True,
                text=True
            )
            if install_process.returncode != 0:
                logging.error(f"❌ Ошибка установки зависимостей: {install_process.stderr}")
                return False
        
        # Запускаем фронтенд
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем запуска
        time.sleep(10)
        
        if process.poll() is None:
            logging.info("✅ Фронтенд запущен")
            
            # Проверяем доступность
            try:
                import requests
                response = requests.get("http://localhost:3000", timeout=5)
                if response.status_code == 200:
                    logging.info("✅ Фронтенд отвечает")
                    process.terminate()
                    return True
                else:
                    logging.error(f"❌ Фронтенд вернул {response.status_code}")
                    process.terminate()
                    return False
            except Exception as e:
                logging.error(f"❌ Не удалось проверить фронтенд: {e}")
                process.terminate()
                return False
        else:
            stdout, stderr = process.communicate()
            logging.error(f"❌ Фронтенд не запустился: {stderr}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Ошибка запуска фронтенда: {e}")
        return False

def main():
    """Основная функция тестирования"""
    logging.info("🧪 Начинаем тестирование сервисов...")
    logging.info("=" * 50)
    
    results = {}
    
    # Тестируем базу данных
    results['database'] = test_database()
    
    # Тестируем API
    results['api'] = test_api()
    
    # Тестируем бота
    results['bot'] = test_bot()
    
    # Тестируем фронтенд
    results['frontend'] = test_frontend()
    
    # Выводим результаты
    logging.info("")
    logging.info("📊 Результаты тестирования:")
    logging.info("=" * 50)
    
    for service, result in results.items():
        status = "✅" if result else "❌"
        logging.info(f"{status} {service}")
    
    # Общий результат
    all_passed = all(results.values())
    if all_passed:
        logging.info("🎉 Все сервисы работают!")
    else:
        logging.error("❌ Некоторые сервисы не работают")
    
    logging.info("=" * 50)

if __name__ == "__main__":
    main() 