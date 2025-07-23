#!/usr/bin/env python3
"""
Скрипт для запуска всех сервисов диет-бота
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
        logging.FileHandler('services.log'),
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
    """Убить процесс на указанном порту"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'connections']):
            try:
                for conn in proc.info['connections']:
                    if conn.laddr.port == port:
                        logging.info(f"Убиваю процесс {proc.info['name']} (PID: {proc.info['pid']}) на порту {port}")
                        proc.terminate()
                        proc.wait(timeout=5)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                continue
    except Exception as e:
        logging.error(f"Ошибка при убийстве процесса на порту {port}: {e}")
    return False

def selective_stop_processes():
    """Остановка процессов по имени"""
    processes_to_kill = ['python', 'node', 'npm', 'nginx']
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            proc_name = proc.info['name'].lower()
            for target in processes_to_kill:
                if target in proc_name:
                    logging.info(f"Останавливаю процесс: {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.restart_attempts = {'api': 0, 'bot': 0, 'frontend': 0, 'nginx': 0}
        self.max_restart_attempts = 3
        self.running = True
        
    def start_api_server(self):
        """Запуск API сервера"""
        try:
            # Проверяем доступность порта 8000
            if not check_port_available(8000):
                logging.warning("Порт 8000 занят, освобождаю...")
                kill_process_on_port(8000)
                time.sleep(2)
                
                # Проверяем еще раз
                if not check_port_available(8000):
                    logging.error("Не удалось освободить порт 8000")
                    return False
            
            logging.info("Запуск API сервера...")
            process = subprocess.Popen(
                [sys.executable, "improved_api_server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.processes['api'] = process
            logging.info(f"API сервер запущен (PID: {process.pid})")
            
            # Ждем немного и проверяем, что процесс действительно запустился
            time.sleep(3)
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                if stderr:
                    logging.error(f"API сервер упал сразу после запуска: {stderr}")
                return False
            
            return True
        except Exception as e:
            logging.error(f"Ошибка запуска API сервера: {e}")
            return False
    
    def start_bot(self):
        """Запуск Telegram бота"""
        try:
            logging.info("Запуск Telegram бота...")
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.processes['bot'] = process
            logging.info(f"Telegram бот запущен (PID: {process.pid})")
            return True
        except Exception as e:
            logging.error(f"Ошибка запуска бота: {e}")
            return False

    def start_frontend(self):
        """Запуск React фронтенда"""
        try:
            # Проверяем доступность порта 5173
            if not check_port_available(5173):
                logging.warning("Порт 5173 занят, освобождаю...")
                kill_process_on_port(5173)
                time.sleep(2)
            
            logging.info("Запуск React фронтенда...")
            
            # Переходим в папку frontend
            frontend_dir = "calorie-love-tracker"
            if not os.path.exists(frontend_dir):
                logging.error(f"Папка {frontend_dir} не найдена")
                return False
            
            # Запускаем npm start
            process = subprocess.Popen(
                ["npm", "start"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.processes['frontend'] = process
            logging.info(f"React фронтенд запущен (PID: {process.pid})")
            return True
        except Exception as e:
            logging.error(f"Ошибка запуска фронтенда: {e}")
            return False

    def start_nginx(self):
        """Запуск Nginx"""
        try:
            # Проверяем доступность порта 80
            if not check_port_available(80):
                logging.warning("Порт 80 занят, освобождаю...")
                kill_process_on_port(80)
                time.sleep(2)
            
            logging.info("Запуск Nginx...")
            
            # Создаем простой nginx.conf если его нет
            nginx_conf = """events {
    worker_connections 1024;
}

http {
    upstream api {
        server 127.0.0.1:8000;
    }

    upstream frontend {
        server 127.0.0.1:5173;
    }

    server {
        listen 80;
        server_name localhost;

        # Проксирование API запросов
        location /api {
            proxy_pass http://api;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Проксирование на frontend
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}"""
            
            with open('nginx.conf', 'w') as f:
                f.write(nginx_conf)
            
            # Запускаем nginx
            process = subprocess.Popen(
                ["nginx", "-c", os.path.abspath("nginx.conf")],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.processes['nginx'] = process
            logging.info(f"Nginx запущен (PID: {process.pid})")
            return True
        except Exception as e:
            logging.error(f"Ошибка запуска Nginx: {e}")
            return False
    
    def check_process(self, name):
        """Проверка состояния процесса"""
        if name not in self.processes:
            return False
        
        process = self.processes[name]
        if process.poll() is None:
            return True
        else:
            # Процесс завершился
            stdout, stderr = process.communicate()
            if stdout:
                logging.info(f"STDOUT {name}: {stdout}")
            if stderr:
                logging.error(f"STDERR {name}: {stderr}")
            logging.warning(f"Процесс {name} завершился (код: {process.returncode})")
            return False
    
    def restart_process(self, name):
        """Перезапуск процесса"""
        if self.restart_attempts[name] >= self.max_restart_attempts:
            logging.error(f"Превышено максимальное количество попыток перезапуска для {name}")
            return False
        
        self.restart_attempts[name] += 1
        logging.info(f"Попытка перезапуска {name} ({self.restart_attempts[name]}/{self.max_restart_attempts})")
        
        if name in self.processes:
            self.stop_process(name)
        
        time.sleep(5)  # Даем больше времени между перезапусками
        
        if name == 'api':
            success = self.start_api_server()
        elif name == 'bot':
            success = self.start_bot()
        elif name == 'frontend':
            success = self.start_frontend()
        elif name == 'nginx':
            success = self.start_nginx()
        else:
            return False
        
        if success:
            self.restart_attempts[name] = 0  # Сбрасываем счетчик при успешном запуске
        
        return success
    
    def stop_process(self, name):
        """Остановка процесса"""
        if name in self.processes:
            process = self.processes[name]
            logging.info(f"Останавливаю {name} (PID: {process.pid})")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            del self.processes[name]
    
    def stop_all(self):
        """Остановка всех процессов"""
        logging.info("Останавливаю все процессы...")
        for name in list(self.processes.keys()):
            self.stop_process(name)
    
    def run(self):
        """Основной цикл управления сервисами"""
        logging.info("Запуск всех сервисов...")
        
        # Останавливаем старые процессы
        selective_stop_processes()
        
        # Запускаем сервисы
        services = ['api', 'bot', 'frontend', 'nginx']
        for service in services:
            if service == 'api':
                self.start_api_server()
            elif service == 'bot':
                self.start_bot()
            elif service == 'frontend':
                self.start_frontend()
            elif service == 'nginx':
                self.start_nginx()
            time.sleep(2)
        
        # Основной цикл мониторинга
        while self.running:
            try:
                for service in services:
                    if not self.check_process(service):
                        logging.warning(f"Процесс {service} упал, перезапускаю...")
                        self.restart_process(service)
                
                time.sleep(10)  # Проверяем каждые 10 секунд
            except Exception as e:
                logging.error(f"Ошибка в основном цикле: {e}")
                time.sleep(5)
        
        self.stop_all()

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logging.info("Получен сигнал остановки")
    if hasattr(signal_handler, 'manager'):
        signal_handler.manager.running = False

if __name__ == "__main__":
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager = ServiceManager()
    signal_handler.manager = manager
    
    try:
        manager.run()
    except KeyboardInterrupt:
        logging.info("Получен сигнал остановки")
        manager.running = False
    finally:
        manager.stop_all()
        logging.info("Все сервисы остановлены") 