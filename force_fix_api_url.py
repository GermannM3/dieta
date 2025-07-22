#!/usr/bin/env python3
"""
Скрипт для принудительного исправления API URL
"""

import os
import re

def fix_api_url_in_file(file_path, old_url, new_url):
    """Исправляет API URL в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем старый URL на новый
        new_content = content.replace(old_url, new_url)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Исправлен API URL в {file_path}")
            return True
        else:
            print(f"ℹ️  API URL в {file_path} уже корректен")
            return False
    except Exception as e:
        print(f"❌ Ошибка при исправлении {file_path}: {e}")
        return False

def main():
    """Основная функция"""
    print("🔧 Принудительное исправление API URL...")
    
    # Файлы для исправления
    files_to_fix = [
        'components/handlers/user_handlers.py',
        'components/handlers/admin_handlers.py',
        'components/handlers/fat_tracker_handlers.py',
        'components/payment_system/payment_handlers.py',
        'components/payment_system/payment_operations.py'
    ]
    
    old_urls = [
        'http://127.0.0.1:8000',
        'http://localhost:8000',
        '127.0.0.1:8000',
        'localhost:8000'
    ]
    
    new_url = 'http://5.129.198.80:8000'
    
    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            for old_url in old_urls:
                if fix_api_url_in_file(file_path, old_url, new_url):
                    fixed_count += 1
        else:
            print(f"⚠️  Файл {file_path} не найден")
    
    print(f"\n📊 Исправлено файлов: {fixed_count}")
    
    if fixed_count > 0:
        print("\n🔄 Требуется перезапуск контейнеров:")
        print("docker-compose down")
        print("docker-compose up -d")
    else:
        print("\n✅ Все API URL уже корректны")

if __name__ == "__main__":
    main() 