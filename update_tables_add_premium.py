#!/usr/bin/env python3
"""
Добавление поля is_premium в таблицы пользователей
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def update_tables():
    """Добавление поля is_premium в таблицы"""
    
    # Получаем параметры подключения
    PGHOST = os.getenv('PGHOST')
    PGUSER = os.getenv('PGUSER')
    PGPASSWORD = os.getenv('PGPASSWORD')
    PGDATABASE = os.getenv('PGDATABASE')
    
    if not all([PGHOST, PGUSER, PGPASSWORD, PGDATABASE]):
        print("❌ Не все параметры подключения найдены в .env!")
        return False
    
    print("🔧 Обновление таблиц...")
    
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(
            host=PGHOST,
            user=PGUSER,
            password=PGPASSWORD,
            database=PGDATABASE,
            sslmode='require'
        )
        cur = conn.cursor()
        
        print("✅ Подключение к базе данных установлено")
        
        # Добавляем поле is_premium в таблицу web_profiles
        try:
            cur.execute("""
                ALTER TABLE web_profiles 
                ADD COLUMN is_premium BOOLEAN DEFAULT FALSE
            """)
            print("✅ Добавлено поле is_premium в web_profiles")
        except psycopg2.errors.DuplicateColumn:
            print("ℹ️ Поле is_premium уже существует в web_profiles")
        
        # Добавляем поле is_premium в таблицу users (для телеграм)
        try:
            cur.execute("""
                ALTER TABLE users 
                ADD COLUMN is_premium BOOLEAN DEFAULT FALSE
            """)
            print("✅ Добавлено поле is_premium в users")
        except psycopg2.errors.DuplicateColumn:
            print("ℹ️ Поле is_premium уже существует в users")
        
        # Добавляем поля для жировой массы в таблицу users
        try:
            cur.execute("""
                ALTER TABLE users 
                ADD COLUMN body_fat_percent FLOAT
            """)
            print("✅ Добавлено поле body_fat_percent в users")
        except psycopg2.errors.DuplicateColumn:
            print("ℹ️ Поле body_fat_percent уже существует в users")
        
        try:
            cur.execute("""
                ALTER TABLE users 
                ADD COLUMN goal_fat_percent FLOAT
            """)
            print("✅ Добавлено поле goal_fat_percent в users")
        except psycopg2.errors.DuplicateColumn:
            print("ℹ️ Поле goal_fat_percent уже существует в users")
        
        conn.commit()
        
        print("✅ Все таблицы обновлены успешно!")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления таблиц: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 Обновление структуры базы данных")
    print("=" * 50)
    
    success = update_tables()
    
    if success:
        print("\n🎉 База данных обновлена!")
        print("✅ Поля для премиум-подписки добавлены")
        print("✅ Поля для жировой массы добавлены")
    else:
        print("\n❌ Ошибка обновления базы данных")

if __name__ == "__main__":
    main() 