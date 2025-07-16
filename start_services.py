import subprocess
import sys
import os
import time
import signal
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('services.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        
    def start_api_server(self):
        """Запуск API сервера"""
        try:
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
        """Запуск фронтенда"""
        try:
            frontend_path = Path("calorie-love-tracker")
            if not frontend_path.exists():
                logging.warning("Папка фронтенда не найдена")
                return False
            
            # Проверяем наличие node_modules
            node_modules = frontend_path / "node_modules"
            if not node_modules.exists():
                logging.info("Установка зависимостей фронтенда...")
                subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
            
            logging.info("Запуск фронтенда...")
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_path,
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
    
    def check_processes(self):
        """Проверка состояния процессов"""
        for name, process in self.processes.items():
            if process.poll() is not None:
                logging.warning(f"Процесс {name} завершился (код: {process.returncode})")
                # Попытка перезапуска
                if name == 'api':
                    self.start_api_server()
                elif name == 'bot':
                    self.start_bot()
                elif name == 'frontend':
                    self.start_frontend()
    
    def stop_all(self):
        """Остановка всех процессов"""
        logging.info("Остановка всех сервисов...")
        self.running = False
        
        for name, process in self.processes.items():
            try:
                logging.info(f"Остановка {name}...")
                process.terminate()
                process.wait(timeout=10)
                logging.info(f"{name} остановлен")
            except subprocess.TimeoutExpired:
                logging.warning(f"Принудительная остановка {name}")
                process.kill()
            except Exception as e:
                logging.error(f"Ошибка остановки {name}: {e}")
    
    def run(self):
        """Основной цикл запуска и мониторинга"""
        # Запускаем сервисы
        if not self.start_api_server():
            logging.error("Не удалось запустить API сервер")
            return
        
        time.sleep(3)  # Даем время API серверу запуститься
        
        if not self.start_bot():
            logging.error("Не удалось запустить бота")
            return
        
        time.sleep(2)  # Даем время боту запуститься
        
        if not self.start_frontend():
            logging.warning("Не удалось запустить фронтенд")
        
        logging.info("Все сервисы запущены!")
        logging.info("API сервер: http://localhost:8000")
        logging.info("Фронтенд: http://localhost:5173")
        logging.info("Бот: активен")
        logging.info("Для остановки нажмите Ctrl+C")
        
        # Мониторинг процессов
        try:
            while self.running:
                self.check_processes()
                time.sleep(10)  # Проверяем каждые 10 секунд
        except KeyboardInterrupt:
            logging.info("Получен сигнал остановки")
        finally:
            self.stop_all()

def signal_handler(signum, frame):
    """Обработчик сигналов для корректной остановки"""
    logging.info("Получен сигнал остановки")
    if hasattr(signal_handler, 'manager'):
        signal_handler.manager.stop_all()
    sys.exit(0)

if __name__ == "__main__":
    # Регистрируем обработчик сигналов
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