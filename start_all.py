#!/usr/bin/env python3
"""
Простой скрипт для запуска всех сервисов диет-бота
"""

import subprocess
import sys
import time
import logging
import signal
import os
import socket
import psutil
from threading import Thread

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('start_all.log'),
        logging.StreamHandler()
    ]
)

def check_port_available(port, host='127.0.0.1'):
    """Проверка доступности порта"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex((host, port))
            return result != 0
    except Exception:
        return False

def kill_process_on_port(port):
    """Убить процесс на порту"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                connections = proc.connections()
                for conn in connections:
                    if conn.laddr.port == port:
                        logging.info(f"Убиваю процесс {proc.info['name']} (PID: {proc.info['pid']}) на порту {port}")
                        proc.terminate()
                        proc.wait(timeout=5)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        logging.error(f"Ошибка при убийстве процесса на порту {port}: {e}")
    return False

def stop_old_processes():
    """Остановка старых процессов"""
    logging.info("🛑 Останавливаем старые процессы...")
    
    # Останавливаем процессы по портам
    for port in [8000, 3000, 80]:
        if not check_port_available(port):
            kill_process_on_port(port)
            time.sleep(1)
    
    # Останавливаем процессы по имени
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmd_str = ' '.join(cmdline)
                    if any(keyword in cmd_str for keyword in ['main.py', 'improved_api_server.py', 'npm start', 'nginx']):
                        logging.info(f"Останавливаю: {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.terminate()
                        proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        logging.error(f"Ошибка при остановке процессов: {e}")

def start_api():
    """Запуск API сервера"""
    logging.info("🚀 Запуск API сервера...")
    
    if not check_port_available(8000):
        kill_process_on_port(8000)
        time.sleep(2)
    
    try:
        process = subprocess.Popen(
            [sys.executable, "improved_api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем немного для запуска
        time.sleep(3)
        
        if process.poll() is None:
            logging.info(f"✅ API сервер запущен (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            logging.error(f"❌ API сервер не запустился: {stderr}")
            return None
    except Exception as e:
        logging.error(f"❌ Ошибка запуска API: {e}")
        return None

def start_frontend():
    """Запуск фронтенда"""
    logging.info("🌐 Запуск фронтенда...")
    
    if not check_port_available(3000):
        kill_process_on_port(3000)
        time.sleep(2)
    
    frontend_dir = "calorie-love-tracker"
    if not os.path.exists(frontend_dir):
        logging.error(f"❌ Директория {frontend_dir} не найдена")
        return None
    
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
                return None
        
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем немного для запуска
        time.sleep(5)
        
        if process.poll() is None:
            logging.info(f"✅ Фронтенд запущен (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            logging.error(f"❌ Фронтенд не запустился: {stderr}")
            return None
    except Exception as e:
        logging.error(f"❌ Ошибка запуска фронтенда: {e}")
        return None

def start_nginx():
    """Запуск nginx"""
    logging.info("🔧 Запуск nginx...")
    
    if not check_port_available(80):
        kill_process_on_port(80)
        time.sleep(2)
    
    nginx_conf = "nginx-prod.conf"
    if not os.path.exists(nginx_conf):
        logging.error(f"❌ Файл конфигурации {nginx_conf} не найден")
        return None
    
    try:
        # Копируем конфигурацию
        subprocess.run(["cp", nginx_conf, "/etc/nginx/sites-available/tvoi-kalkulyator"], check=True)
        subprocess.run(["ln", "-sf", "/etc/nginx/sites-available/tvoi-kalkulyator", "/etc/nginx/sites-enabled/"], check=True)
        
        # Проверяем конфигурацию
        result = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"❌ Ошибка конфигурации nginx: {result.stderr}")
            return None
        
        # Запускаем nginx
        process = subprocess.Popen(
            ["nginx"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(2)
        
        if process.poll() is None:
            logging.info(f"✅ Nginx запущен (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            logging.error(f"❌ Nginx не запустился: {stderr}")
            return None
    except Exception as e:
        logging.error(f"❌ Ошибка запуска nginx: {e}")
        return None

def start_bot():
    """Запуск бота"""
    logging.info("🤖 Запуск бота...")
    
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем немного для запуска
        time.sleep(3)
        
        if process.poll() is None:
            logging.info(f"✅ Бот запущен (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            logging.error(f"❌ Бот не запустился: {stderr}")
            return None
    except Exception as e:
        logging.error(f"❌ Ошибка запуска бота: {e}")
        return None

def check_services():
    """Проверка работы сервисов"""
    logging.info("🔍 Проверяем сервисы...")
    
    services = [
        ("API", "http://localhost:8000/health"),
        ("Фронтенд", "http://localhost:3000"),
        ("Nginx", "http://localhost")
    ]
    
    for name, url in services:
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip() in ["200", "301", "302"]:
                logging.info(f"✅ {name} работает")
            else:
                logging.warning(f"⚠️ {name} не отвечает")
        except Exception as e:
            logging.warning(f"⚠️ Не удалось проверить {name}: {e}")

def main():
    """Основная функция"""
    logging.info("🚀 Запуск Dieta Bot...")
    
    # Останавливаем старые процессы
    stop_old_processes()
    
    # Запускаем сервисы
    processes = {}
    
    # API
    api_process = start_api()
    if api_process:
        processes['api'] = api_process
    
    # Фронтенд
    frontend_process = start_frontend()
    if frontend_process:
        processes['frontend'] = frontend_process
    
    # Nginx
    nginx_process = start_nginx()
    if nginx_process:
        processes['nginx'] = nginx_process
    
    # Бот
    bot_process = start_bot()
    if bot_process:
        processes['bot'] = bot_process
    
    # Проверяем сервисы
    time.sleep(5)
    check_services()
    
    logging.info("🎉 Все сервисы запущены!")
    logging.info("📊 Логи:")
    logging.info("  API: tail -f logs/api.log")
    logging.info("  Фронтенд: tail -f logs/frontend.log")
    logging.info("  Бот: tail -f logs/bot.log")
    logging.info("  Nginx: tail -f /var/log/nginx/tvoi-kalkulyator.error.log")
    logging.info("🌐 Сайт: http://tvoi-kalkulyator.ru")
    logging.info("🤖 Бот: @tvoy_diet_bot")
    
    try:
        # Ждем сигнала завершения
        while True:
            time.sleep(1)
            # Проверяем, что все процессы еще работают
            for name, process in processes.items():
                if process.poll() is not None:
                    logging.warning(f"⚠️ Процесс {name} завершился")
    except KeyboardInterrupt:
        logging.info("🛑 Получен сигнал завершения...")
    finally:
        # Останавливаем все процессы
        logging.info("🛑 Останавливаем все процессы...")
        for name, process in processes.items():
            if process and process.poll() is None:
                logging.info(f"Останавливаю {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        logging.info("✅ Все процессы остановлены")

if __name__ == "__main__":
    main() 