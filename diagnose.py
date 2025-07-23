#!/usr/bin/env python3
"""
Скрипт для диагностики проблем на сервере
"""

import subprocess
import sys
import os
import socket
import psutil
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_file_exists(filename):
    """Проверка существования файла"""
    exists = os.path.exists(filename)
    logging.info(f"📁 {filename}: {'✅' if exists else '❌'}")
    return exists

def check_port_available(port, host='127.0.0.1'):
    """Проверка доступности порта"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            available = result != 0
            logging.info(f"🔌 Порт {port}: {'✅' if available else '❌ (занят)'}")
            return available
    except Exception as e:
        logging.error(f"🔌 Порт {port}: ❌ (ошибка: {e})")
        return False

def check_process_running(process_name):
    """Проверка запущенных процессов"""
    count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and process_name in ' '.join(cmdline):
                count += 1
                logging.info(f"🔄 {process_name}: ✅ (PID: {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if count == 0:
        logging.info(f"🔄 {process_name}: ❌ (не запущен)")
    
    return count

def check_python_modules():
    """Проверка Python модулей"""
    modules = [
        'fastapi', 'aiogram', 'sqlalchemy', 'psutil', 
        'requests', 'pydantic', 'uvicorn', 'python-dotenv'
    ]
    
    for module in modules:
        try:
            __import__(module)
            logging.info(f"🐍 {module}: ✅")
        except ImportError:
            logging.info(f"🐍 {module}: ❌")

def check_node_modules():
    """Проверка Node.js модулей"""
    frontend_dir = "calorie-love-tracker"
    if os.path.exists(frontend_dir):
        node_modules = os.path.join(frontend_dir, "node_modules")
        exists = os.path.exists(node_modules)
        logging.info(f"📦 node_modules: {'✅' if exists else '❌'}")
        return exists
    else:
        logging.info(f"📁 {frontend_dir}: ❌ (не найдена)")
        return False

def check_nginx_config():
    """Проверка конфигурации nginx"""
    try:
        result = subprocess.run(
            ["nginx", "-t"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            logging.info("🔧 nginx config: ✅")
            return True
        else:
            logging.error(f"🔧 nginx config: ❌ ({result.stderr})")
            return False
    except Exception as e:
        logging.error(f"🔧 nginx config: ❌ (ошибка: {e})")
        return False

def check_env_file():
    """Проверка файла .env"""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            required_vars = [
                'TG_TOKEN', 'DATABASE_URL', 'YOOKASSA_SHOP_ID', 
                'YOOKASSA_SECRET_KEY', 'GIGACHAT_ACCESS_TOKEN'
            ]
            
            missing_vars = []
            for var in required_vars:
                if var not in content:
                    missing_vars.append(var)
            
            if missing_vars:
                logging.warning(f"🔑 .env: ⚠️ (отсутствуют: {', '.join(missing_vars)})")
            else:
                logging.info("🔑 .env: ✅")
            return len(missing_vars) == 0
    else:
        logging.error("🔑 .env: ❌ (файл не найден)")
        return False

async def check_database_connection():
    """Проверка подключения к базе данных"""
    try:
        # Импортируем необходимые модули
        from database.init_database import engine
        from sqlalchemy import text
        
        # Пробуем подключиться
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logging.info("🗄️ Database: ✅")
            return True
    except Exception as e:
        logging.error(f"🗄️ Database: ❌ ({e})")
        return False

async def main():
    """Основная функция диагностики"""
    logging.info("🔍 Начинаем диагностику...")
    logging.info("=" * 50)
    
    # Проверяем файлы
    logging.info("📁 Проверка файлов:")
    check_file_exists("main.py")
    check_file_exists("improved_api_server.py")
    check_file_exists("nginx-prod.conf")
    check_file_exists("requirements.txt")
    check_file_exists("package.json")
    
    logging.info("")
    
    # Проверяем порты
    logging.info("🔌 Проверка портов:")
    check_port_available(8000)
    check_port_available(3000)
    check_port_available(80)
    
    logging.info("")
    
    # Проверяем процессы
    logging.info("🔄 Проверка процессов:")
    check_process_running("main.py")
    check_process_running("improved_api_server.py")
    check_process_running("npm start")
    check_process_running("nginx")
    
    logging.info("")
    
    # Проверяем Python модули
    logging.info("🐍 Проверка Python модулей:")
    check_python_modules()
    
    logging.info("")
    
    # Проверяем Node.js модули
    logging.info("📦 Проверка Node.js модулей:")
    check_node_modules()
    
    logging.info("")
    
    # Проверяем nginx
    logging.info("🔧 Проверка nginx:")
    check_nginx_config()
    
    logging.info("")
    
    # Проверяем .env
    logging.info("🔑 Проверка .env:")
    check_env_file()
    
    logging.info("")
    
    # Проверяем базу данных
    logging.info("🗄️ Проверка базы данных:")
    await check_database_connection()
    
    logging.info("")
    logging.info("=" * 50)
    logging.info("✅ Диагностика завершена!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 