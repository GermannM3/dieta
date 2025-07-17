#!/usr/bin/env python3
"""
Быстрое исправление синтаксических ошибок и запуск сервисов
"""

import subprocess
import sys
import os
import time
import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def check_syntax(file_path):
    """Проверка синтаксиса Python файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, file_path, 'exec')
        return True, "OK"
    except SyntaxError as e:
        return False, f"Синтаксическая ошибка в строке {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Ошибка: {e}"

def find_free_port(start_port=8000):
    """Найти свободный порт начиная с start_port"""
    import socket
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def check_files():
    """Проверка основных файлов на синтаксические ошибки"""
    files_to_check = [
        'main.py',
        'improved_api_server.py', 
        'start_all_services.py'
    ]
    
    print("🔍 Проверка файлов на синтаксические ошибки...")
    all_ok = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            is_ok, message = check_syntax(file_path)
            if is_ok:
                print(f"✅ {file_path}: {message}")
            else:
                print(f"❌ {file_path}: {message}")
                all_ok = False
        else:
            print(f"⚠️  {file_path}: файл не найден")
    
    return all_ok

def start_api_server(port=8000):
    """Запуск API сервера на указанном порту"""
    print(f"🚀 Запуск API сервера на порту {port}...")
    
    # Изменяем порт в файле если нужно
    if port != 8000:
        try:
            with open('improved_api_server.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Заменяем порт в uvicorn.run
            content = content.replace('port=8000', f'port={port}')
            
            with open('improved_api_server.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Порт изменен на {port}")
        except Exception as e:
            print(f"❌ Ошибка изменения порта: {e}")
            return None
    
    try:
        process = subprocess.Popen(
            [sys.executable, "improved_api_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Ждем 3 секунды и проверяем
        time.sleep(3)
        if process.poll() is None:
            print(f"✅ API сервер запущен (PID: {process.pid}) на http://127.0.0.1:{port}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ API сервер упал: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Ошибка запуска API сервера: {e}")
        return None

def start_bot():
    """Запуск Telegram бота"""
    print("🤖 Запуск Telegram бота...")
    try:
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(2)
        if process.poll() is None:
            print(f"✅ Telegram бот запущен (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Telegram бот упал: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        return None

def main():
    print("🔧 Быстрое исправление и запуск диетолог-бота")
    print("=" * 50)
    
    # Проверяем синтаксис
    if not check_files():
        print("\n❌ Обнаружены синтаксические ошибки!")
        print("🔍 Проверьте файлы и исправьте ошибки перед запуском")
        return False
    
    print("\n✅ Все файлы синтаксически корректны")
    
    # Находим свободный порт
    free_port = find_free_port(8000)
    if not free_port:
        print("❌ Не удалось найти свободный порт для API сервера")
        return False
    
    if free_port != 8000:
        print(f"⚠️  Порт 8000 занят, используем порт {free_port}")
    
    # Запускаем API сервер
    api_process = start_api_server(free_port)
    if not api_process:
        return False
    
    # Запускаем бота
    bot_process = start_bot()
    if not bot_process:
        # Останавливаем API если бот не запустился
        api_process.terminate()
        return False
    
    print("\n🎉 Все сервисы запущены успешно!")
    print("-" * 50)
    print(f"🌐 API сервер: http://127.0.0.1:{free_port}")
    print(f"📚 API документация: http://127.0.0.1:{free_port}/docs")
    print(f"🤖 Telegram бот: @tvoy_diet_bot")
    print("\nДля остановки нажмите Ctrl+C")
    
    try:
        # Ждем сигнала остановки
        while True:
            if api_process.poll() is not None:
                print("❌ API сервер упал!")
                break
            if bot_process.poll() is not None:
                print("❌ Telegram бот упал!")
                break
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервисов...")
        
    # Останавливаем процессы
    try:
        api_process.terminate()
        bot_process.terminate()
        print("✅ Все сервисы остановлены")
    except:
        pass
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Завершение работы...")
        sys.exit(0) 