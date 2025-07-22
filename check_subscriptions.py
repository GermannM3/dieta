#!/usr/bin/env python3
"""
Скрипт для проверки таблицы подписок
"""

import asyncio
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

async def check_subscription_table():
    """Проверяет таблицу подписок"""
    try:
        # Получаем URL базы данных
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgresql+asyncpg://'):
            database_url = database_url.replace('postgresql+asyncpg://', 'postgresql://', 1)
        
        # Подключаемся к базе данных
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Проверяем, существует ли таблица
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'subscriptions'
            );
        """)
        
        table_exists = cur.fetchone()[0]
        
        if table_exists:
            print("✅ Таблица subscriptions существует")
            
            # Проверяем структуру таблицы
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'subscriptions'
                ORDER BY ordinal_position;
            """)
            
            columns = cur.fetchall()
            print("📋 Структура таблицы subscriptions:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
                
            # Проверяем количество записей
            cur.execute("SELECT COUNT(*) FROM subscriptions;")
            count = cur.fetchone()[0]
            print(f"📊 Количество записей: {count}")
            
        else:
            print("❌ Таблица subscriptions НЕ существует")
            print("🔧 Создаем таблицу...")
            
            # Создаем таблицу
            cur.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    subscription_type VARCHAR(50) NOT NULL,
                    payment_id VARCHAR(255),
                    amount INTEGER NOT NULL,
                    currency VARCHAR(10) DEFAULT 'RUB',
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """)
            
            conn.commit()
            print("✅ Таблица subscriptions создана")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(check_subscription_table()) 