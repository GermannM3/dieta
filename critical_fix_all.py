#!/usr/bin/env python3
"""
КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ВСЕХ ПРОБЛЕМ
===================================
"""

import os
import sys
import subprocess
import time
import logging
import re
import socket
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

def fix_database_url():
    """Исправление DATABASE_URL в .env файле"""
    env_file = ".env"
    
    print("🔧 Исправление DATABASE_URL...")
    
    # Читаем .env файл
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        print("❌ Файл .env не найден!")
        return False
    
    # Исправляем DATABASE_URL
    fixed_lines = []
    found_db_url = False
    
    for line in lines:
        if line.startswith('DATABASE_URL='):
            found_db_url = True
            # Убираем неправильные символы и исправляем формат
            db_url = line.strip().split('=', 1)[1]
            
            # Исправляем распространенные ошибки в URL
            if 'postgres://' in db_url and 'postgresql+asyncpg://' not in db_url:
                db_url = db_url.replace('postgres://', 'postgresql+asyncpg://')
            
            # Убираем лишние символы, которые могут вызывать ошибку парсинга порта
            db_url = re.sub(r'[^\w\-\.\:\/\@\?\=\&]', '', db_url)
            
            fixed_lines.append(f"DATABASE_URL={db_url}\n")
            print(f"✅ DATABASE_URL исправлен: {db_url[:50]}...")
        else:
            fixed_lines.append(line)
    
    if not found_db_url:
        print("❌ DATABASE_URL не найден в .env!")
        return False
    
    # Записываем исправленный файл
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    return True

def check_port(port):
    """Проверка свободен ли порт"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('127.0.0.1', port))
        return result != 0

def kill_process_on_port(port):
    """Убивает процесс на порту (Windows)"""
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.strip().split()
                if len(parts) > 4:
                    pid = parts[-1]
                    print(f"🔫 Убиваю процесс PID {pid} на порту {port}")
                    subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                    time.sleep(1)
                    break
    except Exception as e:
        print(f"⚠️ Ошибка при убийстве процесса на порту {port}: {e}")

def start_service(service_name, script_path, port=None):
    """Запуск сервиса"""
    try:
        if port and not check_port(port):
            print(f"🔌 Порт {port} занят, освобождаю...")
            kill_process_on_port(port)
            time.sleep(2)
        
        print(f"🚀 Запуск {service_name}...")
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(3)  # Даем время запуститься
        
        if process.poll() is None:
            print(f"✅ {service_name} запущен (PID: {process.pid})")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ {service_name} упал сразу после запуска:")
            if stderr:
                print(f"   Ошибка: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка запуска {service_name}: {e}")
        return None

def main():
    """Главная функция исправления"""
    print("🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ВСЕХ ПРОБЛЕМ")
    print("=" * 50)
    
    # 1. Проверка синтаксиса
    print("\n1️⃣ Проверка синтаксиса...")
    files_to_check = ['main.py', 'improved_api_server.py']
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            is_ok, message = check_syntax(file_path)
            if is_ok:
                print(f"✅ {file_path}: {message}")
            else:
                print(f"❌ {file_path}: {message}")
                print("   Остановка - нужно исправить синтаксические ошибки!")
                return False
        else:
            print(f"⚠️ Файл {file_path} не найден")
    
    # 2. Исправление DATABASE_URL
    print("\n2️⃣ Исправление DATABASE_URL...")
    if not fix_database_url():
        print("❌ Не удалось исправить DATABASE_URL!")
        return False
    
    # 3. Остановка старых процессов
    print("\n3️⃣ Остановка старых процессов...")
    kill_process_on_port(8000)  # API
    kill_process_on_port(5173)  # Frontend dev server
    
    # 4. Запуск сервисов
    print("\n4️⃣ Запуск сервисов...")
    
    # Запуск API
    api_process = start_service("API сервер", "improved_api_server.py", 8000)
    if not api_process:
        print("❌ Не удалось запустить API сервер!")
        return False
    
    time.sleep(5)  # Даем API время запуститься
    
    # Проверка health check
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API health check прошел")
        else:
            print(f"⚠️ API health check: статус {response.status_code}")
    except Exception as e:
        print(f"⚠️ API health check не прошел: {e}")
    
    # Запуск бота
    bot_process = start_service("Telegram бот", "main.py")
    if not bot_process:
        print("❌ Не удалось запустить бота!")
        return False
    
    print("\n🎉 ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!")
    print("=" * 50)
    print("🌐 Доступные сервисы:")
    print("   - API: http://127.0.0.1:8000")
    print("   - Health: http://127.0.0.1:8000/health")
    print("   - API Docs: http://127.0.0.1:8000/docs")
    print("   - Telegram бот: активен")
    print("\n📊 Мониторинг:")
    print("   - Логи API: проверьте терминал")
    print("   - Логи бота: проверьте терминал")
    print("\n⚠️ Для остановки: Ctrl+C")
    
    try:
        while True:
            time.sleep(10)
            
            # Проверяем что процессы живы
            if api_process.poll() is not None:
                print("❌ API сервер упал!")
                break
            if bot_process.poll() is not None:
                print("❌ Telegram бот упал!")
                break
            
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервисов...")
        try:
            api_process.terminate()
            bot_process.terminate()
        except:
            pass
        print("✅ Все сервисы остановлены")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"💥 Критическая ошибка: {e}")
        sys.exit(1) 