#!/usr/bin/env python3
"""
Скрипт для добавления таблицы подписок в базу данных
"""

import asyncio
import os
from sqlalchemy import text
from database.init_database import async_session_maker, engine

async def add_subscription_table():
    """Добавляет таблицу подписок в базу данных"""
    try:
        async with engine.begin() as conn:
            # Проверяем, существует ли таблица подписок
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'subscriptions'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("Создание таблицы subscriptions...")
                
                # Создаем таблицу подписок
                await conn.execute(text("""
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
                """))
                
                # Создаем индексы для оптимизации
                await conn.execute(text("""
                    CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
                    CREATE INDEX idx_subscriptions_type ON subscriptions(subscription_type);
                    CREATE INDEX idx_subscriptions_status ON subscriptions(status);
                    CREATE INDEX idx_subscriptions_end_date ON subscriptions(end_date);
                """))
                
                print("✅ Таблица subscriptions создана успешно")
            else:
                print("✅ Таблица subscriptions уже существует")
                
    except Exception as e:
        print(f"❌ Ошибка создания таблицы subscriptions: {e}")
        raise

async def main():
    """Главная функция"""
    print("🔧 Добавление таблицы подписок...")
    await add_subscription_table()
    print("✅ Готово!")

if __name__ == "__main__":
    asyncio.run(main()) 