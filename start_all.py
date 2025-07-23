#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Простой скрипт для запуска всех сервисов Dieta Bot
Использование: python start_all.py
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
    def log(self, message):
        """Логирование с временной меткой"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def stop_processes(self):
        """Остановка всех процессов"""
        self.log("🛑 Останавливаем старые процессы...")
        
        # Останавливаем процессы по имени
        processes_to_kill = [
            "main.py", "improved_api_server.py", 
            "npm start", "node", "nginx"
        ]
        
        for proc_name in processes_to_kill:
            try:
                subprocess.run(f"pkill -f '{proc_name}'", shell=True, capture_output=True)
                self.log(f"✅ Остановлен: {proc_name}")
            except:
                pass
                
        time.sleep(2)
        
    def start_api_server(self):
        """Запуск API сервера"""
        self.log("🌐 Запускаем API сервер на порту 8000...")
        
        try:
            # Запускаем API сервер
            api_process = subprocess.Popen(
                [sys.executable, "improved_api_server.py"],
                stdout=open(self.logs_dir / "api.log", "w"),
                stderr=subprocess.STDOUT,
                cwd=os.getcwd()
            )
            
            self.processes['api'] = api_process
            self.log(f"✅ API сервер запущен (PID: {api_process.pid})")
            
            # Ждем запуска
            time.sleep(3)
            
            # Проверяем API
            try:
                import requests
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    self.log("✅ API сервер работает")
                    return True
                else:
                    self.log("❌ API сервер не отвечает")
                    return False
            except:
                self.log("❌ API сервер не отвечает")
                return False
                
        except Exception as e:
            self.log(f"❌ Ошибка запуска API: {e}")
            return False
            
    def start_frontend(self):
        """Запуск фронтенда"""
        self.log("🎨 Запускаем фронтенд...")
        
        frontend_dir = Path("calorie-love-tracker")
        if not frontend_dir.exists():
            self.log("❌ Папка фронтенда не найдена")
            return False
            
        try:
            # Переходим в папку фронтенда
            os.chdir(frontend_dir)
            
            # Устанавливаем зависимости если нужно
            if not Path("node_modules").exists():
                self.log("📦 Устанавливаем зависимости фронтенда...")
                subprocess.run(["npm", "install"], check=True)
                
            # Собираем проект
            self.log("🔨 Собираем фронтенд...")
            subprocess.run(["npm", "run", "build"], check=True)
            
            # Запускаем фронтенд
            self.log("🌐 Запускаем фронтенд на порту 3000...")
            frontend_process = subprocess.Popen(
                ["npm", "start"],
                stdout=open(Path("../logs/frontend.log"), "w"),
                stderr=subprocess.STDOUT
            )
            
            self.processes['frontend'] = frontend_process
            self.log(f"✅ Фронтенд запущен (PID: {frontend_process.pid})")
            
            # Возвращаемся в корневую папку
            os.chdir("..")
            
            # Ждем запуска
            time.sleep(5)
            
            # Проверяем фронтенд
            try:
                import requests
                response = requests.get("http://localhost:3000", timeout=5)
                if response.status_code == 200:
                    self.log("✅ Фронтенд работает")
                    return True
                else:
                    self.log("❌ Фронтенд не отвечает")
                    return False
            except:
                self.log("❌ Фронтенд не отвечает")
                return False
                
        except Exception as e:
            self.log(f"❌ Ошибка запуска фронтенда: {e}")
            os.chdir("..")  # Возвращаемся в корневую папку
            return False
            
    def setup_nginx(self):
        """Настройка nginx"""
        self.log("🔧 Настраиваем nginx...")
        
        try:
            # Копируем конфигурацию
            subprocess.run([
                "cp", "nginx-prod.conf", 
                "/etc/nginx/sites-available/tvoi-kalkulyator"
            ], check=True)
            
            # Создаем символическую ссылку
            subprocess.run([
                "ln", "-sf", 
                "/etc/nginx/sites-available/tvoi-kalkulyator",
                "/etc/nginx/sites-enabled/"
            ], check=True)
            
            # Удаляем дефолтный сайт
            try:
                os.remove("/etc/nginx/sites-enabled/default")
            except:
                pass
                
            # Проверяем конфигурацию
            subprocess.run(["nginx", "-t"], check=True)
            
            # Перезапускаем nginx
            subprocess.run(["systemctl", "restart", "nginx"], check=True)
            
            self.log("✅ Nginx настроен и перезапущен")
            return True
            
        except Exception as e:
            self.log(f"❌ Ошибка настройки nginx: {e}")
            return False
            
    def start_bot(self):
        """Запуск Telegram бота"""
        self.log("🤖 Запускаем Telegram бота...")
        
        try:
            bot_process = subprocess.Popen(
                [sys.executable, "main.py"],
                stdout=open(self.logs_dir / "bot.log", "w"),
                stderr=subprocess.STDOUT,
                cwd=os.getcwd()
            )
            
            self.processes['bot'] = bot_process
            self.log(f"✅ Бот запущен (PID: {bot_process.pid})")
            return True
            
        except Exception as e:
            self.log(f"❌ Ошибка запуска бота: {e}")
            return False
            
    def save_pids(self):
        """Сохранение PID процессов"""
        for name, process in self.processes.items():
            with open(self.logs_dir / f"{name}.pid", "w") as f:
                f.write(str(process.pid))
                
    def check_services(self):
        """Проверка всех сервисов"""
        self.log("🔍 Проверяем все сервисы...")
        
        checks = [
            ("API (порт 8000)", "http://localhost:8000/health"),
            ("Фронтенд (порт 3000)", "http://localhost:3000"),
            ("Nginx (порт 80)", "http://localhost")
        ]
        
        for name, url in checks:
            try:
                import requests
                if "health" in url:
                    response = requests.get(url, timeout=5)
                    status = response.text if response.status_code == 200 else "НЕ РАБОТАЕТ"
                else:
                    response = requests.get(url, timeout=5)
                    status = response.status_code if response.status_code == 200 else "НЕ РАБОТАЕТ"
                    
                self.log(f"{name}: {status}")
            except:
                self.log(f"{name}: НЕ РАБОТАЕТ")
                
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        self.log("🛑 Получен сигнал завершения, останавливаем сервисы...")
        self.stop_processes()
        sys.exit(0)
        
    def run(self):
        """Основной метод запуска"""
        self.log("🚀 Запуск Dieta Bot...")
        
        # Регистрируем обработчик сигналов
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Останавливаем старые процессы
        self.stop_processes()
        
        # Запускаем сервисы
        success = True
        
        if not self.start_api_server():
            success = False
            
        if not self.start_frontend():
            success = False
            
        if not self.setup_nginx():
            success = False
            
        if not self.start_bot():
            success = False
            
        if success:
            # Сохраняем PID
            self.save_pids()
            
            # Проверяем сервисы
            self.check_services()
            
            self.log("")
            self.log("✅ Все сервисы запущены!")
            self.log("")
            self.log("📋 Информация:")
            self.log("  API сервер: http://localhost:8000")
            self.log("  Фронтенд: http://localhost:3000")
            self.log("  Веб-сайт: http://tvoi-kalkulyator.ru")
            self.log("  Альтернативный домен: http://твой-калькулятор.рф")
            self.log("")
            self.log("📊 Логи:")
            self.log("  API: tail -f logs/api.log")
            self.log("  Фронтенд: tail -f logs/frontend.log")
            self.log("  Бот: tail -f logs/bot.log")
            self.log("  Nginx: tail -f /var/log/nginx/tvoi-kalkulyator.error.log")
            self.log("")
            self.log("🛑 Для остановки: Ctrl+C")
            
            # Ждем завершения
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.log("🛑 Остановка по запросу пользователя...")
                self.stop_processes()
        else:
            self.log("❌ Не все сервисы запустились")
            self.stop_processes()
            sys.exit(1)

if __name__ == "__main__":
    manager = ServiceManager()
    manager.run() 