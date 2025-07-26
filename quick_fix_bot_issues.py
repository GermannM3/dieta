#!/usr/bin/env python3
"""
Быстрое исправление проблем с ботом
"""

import os
import sys
import subprocess
import asyncio
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def run_command(command):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_redis():
    """Проверяет и исправляет проблемы с Redis"""
    print("🔍 Проверка Redis...")
    
    # Проверяем статус Redis через snap
    success, output, error = run_command("sudo snap services redis")
    if success and "active" in output:
        print("✅ Redis работает через snap")
        return True
    
    # Пытаемся запустить Redis через snap
    print("🔄 Запуск Redis через snap...")
    success, output, error = run_command("sudo snap start redis")
    if success:
        print("✅ Redis запущен через snap")
        return True
    
    # Если snap не работает, используем Docker
    print("🔄 Запуск Redis через Docker...")
    success, output, error = run_command("sudo docker ps | grep redis")
    if success and output.strip():
        print("✅ Redis работает в Docker")
        return True
    
    # Создаем Redis контейнер
    success, output, error = run_command("sudo docker run -d --name redis -p 6379:6379 redis:alpine")
    if success:
        print("✅ Redis контейнер создан")
        return True
    
    print("❌ Не удалось запустить Redis")
    return False

def restart_bot():
    """Перезапускает бота"""
    print("🔄 Перезапуск бота...")
    
    # Останавливаем бота
    success, output, error = run_command("sudo systemctl stop bot")
    
    # Убиваем все процессы Python
    run_command("sudo pkill -f 'python.*main'")
    
    # Ждем немного
    import time
    time.sleep(2)
    
    # Запускаем бота
    success, output, error = run_command("sudo systemctl start bot")
    if success:
        print("✅ Бот перезапущен")
        return True
    else:
        print(f"❌ Ошибка запуска бота: {error}")
        return False

def check_bot_status():
    """Проверяет статус бота"""
    print("🔍 Проверка статуса бота...")
    
    success, output, error = run_command("sudo systemctl status bot")
    if success:
        print("📋 Статус бота:")
        print(output)
        
        if "active (running)" in output:
            print("✅ Бот работает")
            return True
        else:
            print("⚠️ Бот не работает")
            return False
    else:
        print(f"❌ Ошибка проверки статуса: {error}")
        return False

def check_bot_logs():
    """Проверяет логи бота"""
    print("🔍 Проверка логов бота...")
    
    success, output, error = run_command("sudo journalctl -u bot --tail=20")
    if success:
        print("📋 Последние логи бота:")
        print(output)
        
        # Проверяем на ошибки
        if "ERROR" in output or "Exception" in output:
            print("⚠️ Обнаружены ошибки в логах")
            return False
        else:
            print("✅ Логи без ошибок")
            return True
    else:
        print(f"❌ Ошибка получения логов: {error}")
        return False

def update_env_file():
    """Обновляет файл .env с новыми настройками YooKassa"""
    print("📝 Обновление настроек YooKassa...")
    
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"❌ Файл {env_file} не найден")
        return False
    
    # Читаем файл
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Обновляем настройки YooKassa
    new_settings = """# ===== YOOKASSA НАСТРОЙКИ =====
YOOKASSA_SHOP_ID=390540012
YOOKASSA_SECRET_KEY=live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA
YOOKASSA_PAYMENT_TOKEN=390540012:LIVE:73839
"""
    
    # Заменяем старые настройки
    lines = content.split('\n')
    new_lines = []
    skip_yookassa = False
    
    for line in lines:
        if line.startswith('# ===== YOOKASSA'):
            skip_yookassa = True
            new_lines.append(new_settings.strip())
        elif skip_yookassa and (line.startswith('YOOKASSA_') or line.startswith('SUBSCRIPTION_')):
            continue
        elif skip_yookassa and line.strip() == '':
            skip_yookassa = False
            new_lines.append(line)
        elif not skip_yookassa:
            new_lines.append(line)
    
    # Записываем обновленный файл
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Настройки YooKassa обновлены")
    return True

def main():
    """Основная функция"""
    print("🚀 Быстрое исправление проблем с ботом")
    print("=" * 50)
    
    # Обновляем настройки
    update_env_file()
    
    # Проверяем Redis
    redis_ok = check_redis()
    
    # Перезапускаем бота
    bot_restarted = restart_bot()
    
    # Ждем немного
    import time
    time.sleep(5)
    
    # Проверяем статус
    bot_status = check_bot_status()
    logs_ok = check_bot_logs()
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТЫ ИСПРАВЛЕНИЯ:")
    print("=" * 50)
    
    print(f"Redis: {'✅ РАБОТАЕТ' if redis_ok else '❌ ПРОБЛЕМЫ'}")
    print(f"Бот перезапущен: {'✅ ДА' if bot_restarted else '❌ НЕТ'}")
    print(f"Статус бота: {'✅ РАБОТАЕТ' if bot_status else '❌ НЕ РАБОТАЕТ'}")
    print(f"Логи бота: {'✅ БЕЗ ОШИБОК' if logs_ok else '⚠️ ЕСТЬ ОШИБКИ'}")
    
    if bot_status and logs_ok:
        print("\n🎉 БОТ УСПЕШНО ИСПРАВЛЕН!")
        print("Теперь можете протестировать бота в Telegram")
    else:
        print("\n⚠️ ЕСТЬ ПРОБЛЕМЫ")
        print("Проверьте логи: sudo journalctl -u bot -f")

if __name__ == "__main__":
    main() 