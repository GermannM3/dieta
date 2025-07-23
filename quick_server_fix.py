#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Быстрое исправление проблем на сервере
Использование: python quick_server_fix.py
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def print_status(message, status="INFO"):
    """Вывод статуса с эмодзи"""
    emoji_map = {
        "INFO": "ℹ️",
        "SUCCESS": "✅", 
        "ERROR": "❌",
        "WARNING": "⚠️",
        "FIX": "🔧"
    }
    emoji = emoji_map.get(status, "ℹ️")
    print(f"{emoji} {message}")

def run_command(command, check=True):
    """Выполнение команды с обработкой ошибок"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print_status(f"Ошибка выполнения команды: {command}", "ERROR")
            print_status(f"Вывод: {result.stderr}", "ERROR")
            return False
        return True
    except Exception as e:
        print_status(f"Ошибка выполнения команды: {e}", "ERROR")
        return False

def check_python_version():
    """Проверка версии Python"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - OK", "SUCCESS")
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} - требуется 3.12+", "ERROR")
        return False

def check_virtual_env():
    """Проверка виртуального окружения"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_status("Виртуальное окружение активировано", "SUCCESS")
        return True
    else:
        print_status("Виртуальное окружение не активировано", "WARNING")
        return False

def check_env_file():
    """Проверка файла .env"""
    env_file = Path(".env")
    if env_file.exists():
        print_status("Файл .env найден", "SUCCESS")
        
        # Проверяем обязательные переменные
        required_vars = [
            "TG_TOKEN", "ADMIN_ID", "DATABASE_URL", 
            "YOOKASSA_SHOP_ID", "YOOKASSA_SECRET_KEY"
        ]
        
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        missing_vars = []
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print_status(f"Отсутствуют переменные: {', '.join(missing_vars)}", "ERROR")
            return False
        else:
            print_status("Все обязательные переменные настроены", "SUCCESS")
            return True
    else:
        print_status("Файл .env не найден", "ERROR")
        return False

def check_dependencies():
    """Проверка зависимостей"""
    print_status("Проверяем зависимости...", "INFO")
    
    # Список критических пакетов
    critical_packages = [
        "aiogram", "fastapi", "sqlalchemy", "asyncpg", 
        "yookassa", "mistralai", "python-dotenv"
    ]
    
    missing_packages = []
    for package in critical_packages:
        try:
            importlib.import_module(package)
            print_status(f"✅ {package} установлен", "SUCCESS")
        except ImportError:
            print_status(f"❌ {package} не установлен", "ERROR")
            missing_packages.append(package)
    
    if missing_packages:
        print_status(f"Отсутствуют пакеты: {', '.join(missing_packages)}", "ERROR")
        return False
    
    return True

def fix_dependencies():
    """Исправление зависимостей"""
    print_status("Исправляем конфликты зависимостей...", "FIX")
    
    commands = [
        "pip cache purge",
        "pip install --upgrade pip",
        "pip uninstall -y aiogram fastapi mistralai pydantic",
        "pip install --no-cache-dir pydantic>=2.10.3",
        "pip install --no-cache-dir fastapi>=0.115,<0.120",
        "pip install --no-cache-dir aiogram>=3.4,<4",
        "pip install --no-cache-dir mistralai>=1.9,<2",
        "pip install --no-cache-dir -r requirements.txt"
    ]
    
    for command in commands:
        print_status(f"Выполняем: {command}", "INFO")
        if not run_command(command):
            return False
    
    print_status("Зависимости исправлены", "SUCCESS")
    return True

def check_database():
    """Проверка подключения к базе данных"""
    print_status("Проверяем подключение к базе данных...", "INFO")
    
    if run_command("python test_db_connection.py"):
        print_status("Подключение к базе данных работает", "SUCCESS")
        return True
    else:
        print_status("Проблемы с подключением к базе данных", "ERROR")
        return False

def check_ports():
    """Проверка занятости портов"""
    print_status("Проверяем порты...", "INFO")
    
    ports = [8000, 3000]
    for port in ports:
        if run_command(f"lsof -i :{port}", check=False):
            print_status(f"Порт {port} занят", "WARNING")
        else:
            print_status(f"Порт {port} свободен", "SUCCESS")

def check_systemd():
    """Проверка systemd сервиса"""
    print_status("Проверяем systemd сервис...", "INFO")
    
    if run_command("systemctl is-active dieta-bot.service", check=False):
        print_status("Сервис dieta-bot.service активен", "SUCCESS")
    else:
        print_status("Сервис dieta-bot.service не активен", "WARNING")
        
        # Проверяем, существует ли файл сервиса
        if Path("/etc/systemd/system/dieta-bot.service").exists():
            print_status("Файл сервиса найден", "SUCCESS")
        else:
            print_status("Файл сервиса не найден", "ERROR")

def main():
    """Основная функция"""
    print_status("🚀 Быстрая диагностика и исправление Dieta Bot", "INFO")
    print("=" * 60)
    
    # Проверки
    checks = [
        ("Версия Python", check_python_version),
        ("Виртуальное окружение", check_virtual_env),
        ("Файл .env", check_env_file),
        ("Зависимости", check_dependencies),
        ("База данных", check_database),
        ("Порты", check_ports),
        ("Systemd сервис", check_systemd)
    ]
    
    failed_checks = []
    
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        if not check_func():
            failed_checks.append(name)
    
    # Исправления
    if failed_checks:
        print(f"\n🔧 Исправляем проблемы...")
        
        if "Зависимости" in failed_checks:
            if fix_dependencies():
                print_status("Зависимости исправлены", "SUCCESS")
            else:
                print_status("Не удалось исправить зависимости", "ERROR")
        
        if "Systemd сервис" in failed_checks:
            print_status("Создаем systemd сервис...", "FIX")
            if run_command("cp dieta-bot.service /etc/systemd/system/"):
                run_command("systemctl daemon-reload")
                run_command("systemctl enable dieta-bot.service")
                print_status("Systemd сервис создан", "SUCCESS")
    
    # Финальные рекомендации
    print(f"\n📋 Рекомендации:")
    print("1. Запустите: ./deploy_server.sh")
    print("2. Проверьте логи: journalctl -u dieta-bot.service -f")
    print("3. Проверьте API: curl http://localhost:8000/health")
    print("4. Проверьте фронтенд: curl -I http://localhost:3000")
    
    if not failed_checks:
        print_status("🎉 Все проверки пройдены успешно!", "SUCCESS")
    else:
        print_status(f"⚠️ Проблемы найдены: {', '.join(failed_checks)}", "WARNING")

if __name__ == "__main__":
    main() 