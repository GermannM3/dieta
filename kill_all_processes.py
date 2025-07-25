#!/usr/bin/env python3
"""
Экстренный скрипт для принудительного убийства всех процессов
"""

import os
import subprocess
import signal
import psutil
import time

def run_command(cmd, description=""):
    """Выполнить команду и вывести результат"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout}")
        if result.stderr:
            print(f"⚠️ {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def kill_process_by_pid(pid):
    """Убить процесс по PID"""
    try:
        process = psutil.Process(pid)
        print(f"🔥 Убиваю процесс {pid} ({process.name()})")
        
        # Сначала пытаемся terminate
        process.terminate()
        try:
            process.wait(timeout=3)
            print(f"✅ Процесс {pid} завершен")
            return True
        except psutil.TimeoutExpired:
            # Если не завершился, убиваем принудительно
            process.kill()
            process.wait(timeout=2)
            print(f"✅ Процесс {pid} принудительно убит")
            return True
    except psutil.NoSuchProcess:
        print(f"⚠️ Процесс {pid} уже не существует")
        return True
    except Exception as e:
        print(f"❌ Ошибка убийства процесса {pid}: {e}")
        return False

def kill_all_python_processes():
    """Убить все процессы Python"""
    print("🔥 Убиваю все процессы Python...")
    
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'main.py' in cmdline or 'improved_api_server' in cmdline or 'start_all_services' in cmdline:
                    print(f"🎯 Найден процесс Python: {proc.info['pid']} - {cmdline}")
                    if kill_process_by_pid(proc.info['pid']):
                        killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print(f"✅ Убито {killed_count} процессов Python")
    return killed_count

def kill_all_npm_processes():
    """Убить все процессы npm/node"""
    print("🔥 Убиваю все процессы npm/node...")
    
    killed_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and any(name in proc.info['name'].lower() for name in ['npm', 'node', 'vite']):
                cmdline = ' '.join(proc.info['cmdline'] or [])
                print(f"🎯 Найден процесс npm/node: {proc.info['pid']} - {cmdline}")
                if kill_process_by_pid(proc.info['pid']):
                    killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print(f"✅ Убито {killed_count} процессов npm/node")
    return killed_count

def force_kill_by_port(port):
    """Принудительно убить процессы на порту"""
    print(f"🔥 Принудительно освобождаю порт {port}...")
    
    try:
        # Найти процессы на порту
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.pid:
                print(f"🎯 Найден процесс на порту {port}: {conn.pid}")
                kill_process_by_pid(conn.pid)
    except Exception as e:
        print(f"❌ Ошибка освобождения порта {port}: {e}")

def main():
    print("🚨 ЭКСТРЕННОЕ УБИЙСТВО ВСЕХ ПРОЦЕССОВ")
    print("=" * 50)
    
    # 1. Остановить systemd сервисы
    print("\n1️⃣ Останавливаю systemd сервисы...")
    run_command("sudo systemctl stop api frontend nginx bot", "Остановка systemd сервисов")
    
    # 2. Убить все процессы Python
    print("\n2️⃣ Убиваю все процессы Python...")
    killed_python = kill_all_python_processes()
    
    # 3. Убить все процессы npm/node
    print("\n3️⃣ Убиваю все процессы npm/node...")
    killed_npm = kill_all_npm_processes()
    
    # 4. Принудительно освободить порты
    print("\n4️⃣ Принудительно освобождаю порты...")
    force_kill_by_port(8000)
    force_kill_by_port(80)
    force_kill_by_port(5173)
    
    # 5. Дополнительные команды убийства
    print("\n5️⃣ Дополнительные команды убийства...")
    run_command("sudo pkill -9 -f 'python.*main.py'", "Принудительное убийство main.py")
    run_command("sudo pkill -9 -f 'python.*main'", "Принудительное убийство main")
    run_command("sudo pkill -9 -f 'python.*improved_api_server'", "Принудительное убийство API")
    run_command("sudo pkill -9 -f 'python.*start_all_services'", "Принудительное убийство start_all_services")
    run_command("sudo pkill -9 -f 'npm'", "Принудительное убийство npm")
    run_command("sudo pkill -9 -f 'vite'", "Принудительное убийство vite")
    run_command("sudo pkill -9 -f 'node'", "Принудительное убийство node")
    
    # 6. Проверить что все убиты
    print("\n6️⃣ Проверяю что все процессы убиты...")
    time.sleep(2)
    
    remaining_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name']:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(keyword in cmdline for keyword in ['main.py', 'improved_api_server', 'start_all_services']):
                    remaining_processes.append(f"{proc.info['pid']} - {cmdline}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if remaining_processes:
        print("⚠️ Остались процессы:")
        for proc in remaining_processes:
            print(f"   {proc}")
        
        print("\n🔥 Принудительное убийство оставшихся процессов...")
        for proc in remaining_processes:
            pid = proc.split(' - ')[0]
            try:
                kill_process_by_pid(int(pid))
            except:
                pass
    else:
        print("✅ Все процессы убиты!")
    
    # 7. Финальная проверка
    print("\n7️⃣ Финальная проверка...")
    run_command("ps aux | grep -E '(python|npm|node)' | grep -v grep", "Проверка оставшихся процессов")
    run_command("netstat -tlnp | grep -E '(8000|80|5173)'", "Проверка занятых портов")
    
    print("\n🎯 ГОТОВО! Все процессы убиты!")
    print("Теперь можно запускать сервисы заново:")

if __name__ == "__main__":
    main() 