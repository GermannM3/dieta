#!/usr/bin/env python3
"""
Простой скрипт для создания таблицы подписок
"""

import asyncio
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

async def create_subscription_table():
    """Создает таблицу подписок"""
    try:
        # Получаем URL базы данных
        database_url = os.getenv('DATABASE_URL')
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        
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
        
        if not table_exists:
            print("Создание таблицы subscriptions...")
            
            # Создаем таблицу подписок
            cur.execute("""
                CREATE TABLE subscriptions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL REFERENCES users(tg_id),
                    subscription_type VARCHAR NOT NULL,
                    payment_id VARCHAR NOT NULL,
                    amount FLOAT NOT NULL,
                    currency VARCHAR DEFAULT 'RUB',
                    status VARCHAR DEFAULT 'pending',
                    start_date TIMESTAMP NOT NULL,
                    end_date TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Создаем индексы
            cur.execute("CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);")
            cur.execute("CREATE INDEX idx_subscriptions_type ON subscriptions(subscription_type);")
            cur.execute("CREATE INDEX idx_subscriptions_status ON subscriptions(status);")
            cur.execute("CREATE INDEX idx_subscriptions_end_date ON subscriptions(end_date);")
            
            conn.commit()
            print("✅ Таблица subscriptions создана успешно")
        else:
            print("✅ Таблица subscriptions уже существует")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка создания таблицы: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_subscription_table()) 