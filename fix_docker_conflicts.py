#!/usr/bin/env python3
"""
Скрипт для исправления конфликтов Docker контейнеров
"""

import subprocess
import sys
import os

def run_command(command):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_port_usage():
    """Проверяет какие процессы используют порт 80"""
    print("🔍 Проверка использования порта 80...")
    
    success, output, error = run_command("netstat -tlnp | grep :80")
    if success and output:
        print("⚠️  Порт 80 используется:")
        print(output)
        return True
    else:
        print("✅ Порт 80 свободен")
        return False

def check_docker_containers():
    """Проверяет запущенные Docker контейнеры"""
    print("\n🔍 Проверка запущенных Docker контейнеров...")
    
    success, output, error = run_command("docker ps -a")
    if success:
        print("📋 Запущенные контейнеры:")
        print(output)
        
        # Проверяем есть ли контейнеры с портом 80
        if ":80->" in output or "0.0.0.0:80" in output:
            print("⚠️  Найдены контейнеры использующие порт 80")
            return True
        else:
            print("✅ Нет контейнеров использующих порт 80")
            return False
    else:
        print(f"❌ Ошибка проверки контейнеров: {error}")
        return False

def stop_conflicting_containers():
    """Останавливает конфликтующие контейнеры"""
    print("\n🛑 Остановка конфликтующих контейнеров...")
    
    # Останавливаем все контейнеры с портом 80
    success, output, error = run_command("docker ps -q --filter 'publish=80' | xargs -r docker stop")
    if success:
        print("✅ Конфликтующие контейнеры остановлены")
    else:
        print(f"⚠️  Не удалось остановить контейнеры: {error}")
    
    # Останавливаем все контейнеры проекта
    success, output, error = run_command("docker-compose down")
    if success:
        print("✅ Все контейнеры проекта остановлены")
    else:
        print(f"⚠️  Не удалось остановить контейнеры проекта: {error}")

def clean_docker_system():
    """Очищает неиспользуемые Docker ресурсы"""
    print("\n🧹 Очистка Docker системы...")
    
    success, output, error = run_command("docker system prune -f")
    if success:
        print("✅ Docker система очищена")
    else:
        print(f"⚠️  Не удалось очистить Docker систему: {error}")

def rebuild_and_start():
    """Пересобирает и запускает контейнеры"""
    print("\n🔨 Пересборка и запуск контейнеров...")
    
    # Пересобираем образы
    success, output, error = run_command("docker-compose build --no-cache")
    if success:
        print("✅ Образы пересобраны")
    else:
        print(f"❌ Ошибка пересборки: {error}")
        return False
    
    # Запускаем контейнеры
    success, output, error = run_command("docker-compose up -d")
    if success:
        print("✅ Контейнеры запущены")
        return True
    else:
        print(f"❌ Ошибка запуска: {error}")
        return False

def check_services():
    """Проверяет статус сервисов"""
    print("\n🔍 Проверка статуса сервисов...")
    
    success, output, error = run_command("docker-compose ps")
    if success:
        print("📋 Статус сервисов:")
        print(output)
        
        # Проверяем что все сервисы запущены
        if "Up" in output and "Exit" not in output:
            print("✅ Все сервисы запущены")
            return True
        else:
            print("⚠️  Не все сервисы запущены")
            return False
    else:
        print(f"❌ Ошибка проверки статуса: {error}")
        return False

def main():
    """Основная функция"""
    print("🚀 Исправление конфликтов Docker контейнеров...")
    print("=" * 60)
    
    # Проверяем использование порта 80
    port_conflict = check_port_usage()
    
    # Проверяем Docker контейнеры
    container_conflict = check_docker_containers()
    
    if port_conflict or container_conflict:
        print("\n⚠️  Обнаружены конфликты!")
        
        # Останавливаем конфликтующие контейнеры
        stop_conflicting_containers()
        
        # Очищаем Docker систему
        clean_docker_system()
        
        # Пересобираем и запускаем
        if rebuild_and_start():
            # Проверяем статус
            check_services()
        else:
            print("❌ Не удалось запустить контейнеры")
    else:
        print("\n✅ Конфликтов не обнаружено")
        
        # Просто перезапускаем контейнеры
        success, output, error = run_command("docker-compose down")
        if success:
            print("✅ Контейнеры остановлены")
        
        if rebuild_and_start():
            check_services()
        else:
            print("❌ Не удалось запустить контейнеры")
    
    print("\n" + "=" * 60)
    print("📋 РЕКОМЕНДАЦИИ:")
    print("1. Проверьте логи: docker-compose logs")
    print("2. Проверьте API: curl http://localhost:8000/health")
    print("3. Проверьте фронтенд: curl http://localhost:3000")
    print("4. Если проблемы остаются, перезагрузите сервер")

if __name__ == "__main__":
    main() 