#!/usr/bin/env python3
"""
Скрипт для полной остановки всех процессов бота и API
"""

import subprocess
import sys
import time
import os

def kill_process_on_port(port):
    """Убить процесс, занимающий указанный порт"""
    try:
        # Получаем PID процесса на порту
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=True)
                            print(f"✅ Остановлен процесс PID {pid} на порту {port}")
                        except subprocess.CalledProcessError:
                            print(f"❌ Не удалось остановить процесс PID {pid}")
        else:
            print(f"✅ Порт {port} свободен")
            
    except Exception as e:
        print(f"❌ Ошибка при освобождении порта {port}: {e}")

def kill_python_processes_by_script():
    """Убить Python процессы через taskkill"""
    try:
        # Убиваем все python процессы
        result = subprocess.run('taskkill /F /IM python.exe', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Остановлены Python процессы")
            return 1
        else:
            print("✅ Нет активных Python процессов")
            return 0
    except Exception as e:
        print(f"❌ Ошибка остановки Python процессов: {e}")
        return 0

def main():
    print("🛑 Остановка всех сервисов...")
    print("=" * 50)
    
    # 1. Остановка процессов по скриптам
    print("📋 Поиск и остановка Python процессов...")
    killed_count = kill_python_processes_by_script()
    
    # 2. Освобождение портов
    print("\n🔌 Освобождение портов...")
    kill_process_on_port(8000)  # API сервер
    kill_process_on_port(5173)  # Frontend (если запущен)
    
    # 3. Дополнительная очистка
    print("\n🧹 Дополнительная очистка...")
    try:
        # Убиваем все оставшиеся python процессы (осторожно!)
        result = subprocess.run('taskkill /F /IM python.exe', shell=True, capture_output=True)
        if result.returncode == 0:
            print("✅ Остановлены все оставшиеся Python процессы")
        else:
            print("✅ Дополнительных Python процессов не найдено")
    except:
        pass
    
    # 4. Финальная проверка
    time.sleep(2)
    print("\n🔍 Финальная проверка...")
    
    # Проверяем порт 8000
    result = subprocess.run('netstat -ano | findstr :8000', shell=True, capture_output=True)
    if result.stdout:
        print("⚠️  Порт 8000 все еще занят")
    else:
        print("✅ Порт 8000 свободен")
    
    print("\n" + "=" * 50)
    print("✅ Все сервисы остановлены!")
    print("💡 Теперь можете безопасно запускать start_all_services.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Остановка прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1) 