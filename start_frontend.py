#!/usr/bin/env python3
"""
Скрипт для запуска фронтенда
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

def start_frontend():
    """Запуск фронтенда"""
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
        logging.info("🌐 Запускаем фронтенд...")
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем запуска
        time.sleep(5)
        
        if process.poll() is None:
            logging.info("✅ Фронтенд запущен (PID: {})".format(process.pid))
            logging.info("🌐 Сайт доступен по адресу: http://localhost:3000")
            return True
        else:
            stdout, stderr = process.communicate()
            logging.error(f"❌ Фронтенд не запустился: {stderr}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Ошибка запуска фронтенда: {e}")
        return False

if __name__ == "__main__":
    start_frontend() 