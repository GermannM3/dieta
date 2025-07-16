#!/usr/bin/env python3
"""
Единый скрипт запуска всех сервисов диетолога
"""

import subprocess
import time
import signal
import sys
import os
import logging
import socket
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('services.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def check_port_available(port, host='127.0.0.1'):
    """Проверка доступности порта"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex((host, port))
            return result != 0  # Порт свободен если не удалось подключиться
    except Exception:
        return True  # Считаем порт свободным при ошибке

def kill_process_on_port(port):
    """Убивает процесс, занимающий указанный порт"""
    try:
        # Для Windows
        if os.name == 'nt':
            result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.strip().split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        logging.info(f"Останавливаю процесс PID {pid} на порту {port}")
                        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                        time.sleep(1)
                        break
    except Exception as e:
        logging.error(f"Ошибка при остановке процесса на порту {port}: {e}")

def selective_stop_processes():
    """Избирательная остановка только целевых процессов"""
    print("🛑 Остановка существующих сервисов...")
    
    # Останавливаем процессы на портах
    print("🔌 Освобождение портов...")
    kill_process_on_port(8000)  # API сервер
    kill_process_on_port(5173)  # Frontend (если запущен)
    
    # Поиск и остановка конкретных скриптов
    try:
        result = subprocess.run(['wmic', 'process', 'get', 'ProcessId,CommandLine'], 
                              capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        target_scripts = ['main.py', 'improved_api_server.py']
        pids_to_kill = []
        
        for line in lines:
            for script in target_scripts:
                if script in line and 'python' in line.lower():
                    parts = line.strip().split()
                    if parts:
                        try:
                            pid = parts[-1]
                            if pid.isdigit():
                                pids_to_kill.append((pid, script))
                        except:
                            continue
        
        for pid, script in pids_to_kill:
            try:
                subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                print(f"✅ Остановлен процесс {script} (PID: {pid})")
            except:
                pass
                
    except Exception as e:
        print(f"⚠️  Ошибка при поиске процессов: {e}")
    
    print("✅ Предварительная очистка завершена")

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        self.restart_attempts = {'api': 0, 'bot': 0}
        self.max_restart_attempts = 3
        
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
        else:
            return False
        
        if success:
            self.restart_attempts[name] = 0  # Сбрасываем счетчик при успешном запуске
        
        return success
    
    def stop_process(self, name):
        """Остановка процесса"""
        if name in self.processes:
            process = self.processes[name]
            try:
                process.terminate()
                process.wait(timeout=5)
                logging.info(f"{name} остановлен")
            except subprocess.TimeoutExpired:
                process.kill()
                logging.warning(f"{name} принудительно остановлен")
            except Exception as e:
                logging.error(f"Ошибка остановки {name}: {e}")
            del self.processes[name]
    
    def stop_all(self):
        """Остановка всех процессов"""
        logging.info("Остановка всех сервисов...")
        for name in list(self.processes.keys()):
            self.stop_process(name)
    
    def run(self):
        """Основной цикл управления сервисами"""
        # Запускаем сервисы
        if not self.start_api_server():
            logging.error("Не удалось запустить API сервер")
            return
        
        time.sleep(2)  # Даем время API серверу запуститься
        
        if not self.start_bot():
            logging.error("Не удалось запустить бота")
            self.stop_all()
            return
        
        logging.info("Все сервисы запущены")
        logging.info("🔄 Система мониторинга активирована - бот будет автоматически перезапускаться при сбоях")
        
        # Основной цикл мониторинга
        consecutive_failures = {'api': 0, 'bot': 0}
        while self.running:
            try:
                # Проверяем состояние процессов
                for name in ['api', 'bot']:
                    if not self.check_process(name):
                        consecutive_failures[name] += 1
                        
                        if consecutive_failures[name] <= 5:  # Пытаемся перезапустить до 5 раз подряд
                            logging.warning(f"🔄 Автоматический перезапуск {name} (попытка {consecutive_failures[name]}/5)...")
                            if self.restart_process(name):
                                consecutive_failures[name] = 0  # Сбрасываем счетчик при успехе
                                logging.info(f"✅ Сервис {name} успешно перезапущен")
                            else:
                                logging.error(f"❌ Не удалось перезапустить {name}")
                        else:
                            logging.error(f"💀 Превышено максимальное количество попыток перезапуска для {name}")
                            if name == 'bot':
                                logging.error("🚨 Критическая ошибка: бот не может быть перезапущен!")
                    else:
                        consecutive_failures[name] = 0  # Сбрасываем счетчик при успешной проверке
                
                time.sleep(15)  # Проверяем каждые 15 секунд для экономии ресурсов
                
            except KeyboardInterrupt:
                logging.info("Получен сигнал остановки")
                self.running = False
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
    print("🤖 Система управления Диетолог-ботом")
    print("=" * 50)
    
    # Сначала останавливаем только целевые процессы
    selective_stop_processes()
    time.sleep(3)  # Даем время на полную остановку
    
    print("\n🚀 Запуск новых сервисов...")
    print("-" * 50)
    
    # Регистрируем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Создаем и запускаем менеджер сервисов
    manager = ServiceManager()
    signal_handler.manager = manager
    
    try:
        manager.run()
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        manager.stop_all()
        sys.exit(1) 