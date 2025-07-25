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
        logging.error(f"Ошибка при убийстве процесса на порту {port}: {e}")
    return False

def selective_stop_processes():
    """Остановка старых процессов"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline:
                    cmd_str = ' '.join(cmdline)
                    if any(keyword in cmd_str for keyword in ['main.py', 'improved_api_server.py', 'npm start', 'nginx']):
                        logging.info(f"Останавливаю старый процесс: {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.terminate()
                        proc.wait(timeout=5)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception as e:
        logging.error(f"Ошибка при остановке старых процессов: {e}")

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        self.restart_attempts = {'api': 0, 'bot': 0, 'frontend': 0, 'nginx': 0}
        self.max_restart_attempts = 3
        self._shutdown_event = False

    def start_api_server(self):
        """Запуск API сервера"""
        try:
            # Проверяем доступность порта 8000
            if not check_port_available(8000):
                logging.warning("Порт 8000 занят, освобождаю...")
                kill_process_on_port(8000)
                time.sleep(2)
            
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
            return True
        except Exception as e:
            logging.error(f"Ошибка запуска API сервера: {e}")
            return False

    def start_bot(self):
        """Запуск бота"""
        try:
            logging.info("Запуск бота...")
            
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            self.processes['bot'] = process
            logging.info(f"Бот запущен (PID: {process.pid})")
            return True
        except Exception as e:
            logging.error(f"Ошибка запуска бота: {e}")
            return False

    def start_frontend(self):
        """Запуск фронтенда"""
        try:
            # Проверяем доступность порта 5173
            if not check_port_available(5173):
                logging.warning("Порт 5173 занят, освобождаю...")
                kill_process_on_port(5173)
                time.sleep(2)
            
            logging.info("Запуск фронтенда...")
            
            # Переходим в директорию фронтенда
            frontend_dir = "calorie-love-tracker"
            if not os.path.exists(frontend_dir):
                logging.error(f"Директория {frontend_dir} не найдена")
                return False
            
            # Проверяем наличие node_modules
            if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
                logging.info("Устанавливаем зависимости фронтенда...")
                install_process = subprocess.run(
                    ["npm", "install"],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True
                )
                if install_process.returncode != 0:
                    logging.error(f"Ошибка установки зависимостей: {install_process.stderr}")
                    return False
            
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
            logging.info(f"Фронтенд запущен (PID: {process.pid})")
            return True
        except Exception as e:
            logging.error(f"Ошибка запуска фронтенда: {e}")
            return False

    def start_nginx(self):
        """Запуск nginx"""
        try:
            # Проверяем доступность порта 80
            if not check_port_available(80):
                logging.warning("Порт 80 занят, освобождаю...")
                kill_process_on_port(80)
                time.sleep(2)
            
            logging.info("Запуск nginx...")
            
            # Проверяем наличие конфигурации nginx
            nginx_conf = "nginx.conf"
            if not os.path.exists(nginx_conf):
                logging.error(f"Файл конфигурации {nginx_conf} не найден")
                return False
            
            process = subprocess.Popen(
                ["nginx", "-c", os.path.abspath(nginx_conf)],
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
            logging.error(f"Ошибка запуска nginx: {e}")
            return False

    def check_process(self, name):
        """Проверка состояния процесса"""
        if name not in self.processes:
            return False
        
        process = self.processes[name]
        if process.poll() is None:
            return True
        else:
            logging.warning(f"Процесс {name} завершился с кодом {process.returncode}")
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
            
            # Сначала пытаемся graceful shutdown
            process.terminate()
            try:
                process.wait(timeout=10)  # Увеличиваем таймаут
            except subprocess.TimeoutExpired:
                logging.warning(f"Процесс {name} не завершился gracefully, принудительно завершаю...")
                process.kill()
                process.wait()
            
            del self.processes[name]
    
    def stop_all(self):
        """Остановка всех процессов"""
        logging.info("Останавливаю все процессы...")
        for name in list(self.processes.keys()):
            self.stop_process(name)
    
    def graceful_shutdown(self):
        """Graceful shutdown всех процессов"""
        logging.info("Начинаю graceful shutdown...")
        self._shutdown_event = True
        self.running = False
        
        # Даем время на graceful shutdown
        time.sleep(2)
        
        # Останавливаем все процессы
        self.stop_all()
        logging.info("Graceful shutdown завершен")
    
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
        while self.running and not self._shutdown_event:
            try:
                for service in services:
                    if not self.check_process(service):
                        logging.warning(f"Процесс {service} упал, перезапускаю...")
                        self.restart_process(service)
                
                time.sleep(10)  # Проверяем каждые 10 секунд
            except Exception as e:
                logging.error(f"Ошибка в основном цикле: {e}")
                time.sleep(5)
        
        if self._shutdown_event:
            self.graceful_shutdown()
        else:
            self.stop_all()

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logging.info(f"Получен сигнал {signum}, начинаю graceful shutdown...")
    if hasattr(signal_handler, 'manager'):
        signal_handler.manager.graceful_shutdown()

if __name__ == "__main__":
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # На Windows также обрабатываем SIGBREAK
    if hasattr(signal, 'SIGBREAK'):
        signal.signal(signal.SIGBREAK, signal_handler)
    
    manager = ServiceManager()
    signal_handler.manager = manager
    
    try:
        manager.run()
    except KeyboardInterrupt:
        logging.info("Получен KeyboardInterrupt, начинаю graceful shutdown...")
        manager.graceful_shutdown()
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        manager.stop_all()
    finally:
        logging.info("Все сервисы остановлены") 