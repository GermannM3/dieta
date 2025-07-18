#!/usr/bin/env python3
"""
Создание таблиц для веб-аутентификации в Neon PostgreSQL (прямое подключение)
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_web_tables():
    """Создание таблиц для веб-пользователей"""
    
    # Получаем параметры подключения из переменных окружения
    PGHOST = os.getenv('PGHOST')
    PGUSER = os.getenv('PGUSER')
    PGPASSWORD = os.getenv('PGPASSWORD')
    PGDATABASE = os.getenv('PGDATABASE')
    
    if not all([PGHOST, PGUSER, PGPASSWORD, PGDATABASE]):
        print("❌ Не все параметры подключения найдены в .env!")
        print(f"PGHOST: {PGHOST}")
        print(f"PGUSER: {PGUSER}")
        print(f"PGPASSWORD: {'*' * len(PGPASSWORD) if PGPASSWORD else 'None'}")
        print(f"PGDATABASE: {PGDATABASE}")
        return False
    
    print("🔧 Создание таблиц для веб-аутентификации...")
    print(f"📊 Хост: {PGHOST}")
    print(f"📊 База данных: {PGDATABASE}")
    print(f"📊 Пользователь: {PGUSER}")
    
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
        
        # SQL для создания таблиц
        create_tables_sql = """
        -- Таблица веб-пользователей
        CREATE TABLE IF NOT EXISTS web_users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            name VARCHAR(100),
            is_confirmed BOOLEAN DEFAULT FALSE,
            confirmation_code VARCHAR(10),
            reset_code VARCHAR(10),
            reset_code_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Индекс для email
        CREATE INDEX IF NOT EXISTS idx_web_users_email ON web_users(email);

        -- Таблица профилей веб-пользователей
        CREATE TABLE IF NOT EXISTS web_profiles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES web_users(id) ON DELETE CASCADE,
            name VARCHAR(100),
            gender VARCHAR(10) CHECK (gender IN ('male', 'female')),
            age INTEGER CHECK (age > 0 AND age < 150),
            weight DECIMAL(5,2) CHECK (weight > 0),
            height DECIMAL(5,2) CHECK (height > 0),
            activity_level DECIMAL(3,2) CHECK (activity_level >= 1.0 AND activity_level <= 3.0),
            daily_target DECIMAL(7,2),
            water_target INTEGER DEFAULT 2000,
            steps_target INTEGER DEFAULT 10000,
            mood VARCHAR(20) CHECK (mood IN ('excellent', 'good', 'okay', 'bad', 'terrible')),
            water_ml INTEGER DEFAULT 0,
            streak_days INTEGER DEFAULT 0,
            score INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Индекс для user_id
        CREATE INDEX IF NOT EXISTS idx_web_profiles_user_id ON web_profiles(user_id);

        -- Таблица приемов пищи веб-пользователей
        CREATE TABLE IF NOT EXISTS web_meals (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES web_users(id) ON DELETE CASCADE,
            date VARCHAR(10) NOT NULL, -- YYYY-MM-DD
            time VARCHAR(8), -- HH:MM:SS
            food_name VARCHAR(200) NOT NULL,
            weight_grams DECIMAL(7,2) NOT NULL CHECK (weight_grams > 0),
            calories DECIMAL(7,2) NOT NULL CHECK (calories >= 0),
            protein DECIMAL(7,2) DEFAULT 0,
            fat DECIMAL(7,2) DEFAULT 0,
            carbs DECIMAL(7,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW()
        );

        -- Индексы для web_meals
        CREATE INDEX IF NOT EXISTS idx_web_meals_user_id ON web_meals(user_id);
        CREATE INDEX IF NOT EXISTS idx_web_meals_date ON web_meals(date);
        CREATE INDEX IF NOT EXISTS idx_web_meals_user_date ON web_meals(user_id, date);

        -- Таблица пресетов веб-пользователей
        CREATE TABLE IF NOT EXISTS web_presets (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES web_users(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            meal_type VARCHAR(20) CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
            food_items JSONB NOT NULL,
            total_calories DECIMAL(7,2) DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        -- Индекс для web_presets
        CREATE INDEX IF NOT EXISTS idx_web_presets_user_id ON web_presets(user_id);
        """
        
        print("📝 Выполнение SQL запросов...")
        cur.execute(create_tables_sql)
        conn.commit()
        print("✅ Таблицы созданы успешно!")
        
        # Проверяем созданные таблицы
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'web_%'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        print("\n📋 Созданные таблицы:")
        for table in tables:
            print(f"  ✅ {table[0]}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🗄️ Настройка базы данных для веб-аутентификации")
    print("=" * 50)
    
    success = create_web_tables()
    
    if success:
        print("\n🎉 База данных готова!")
        print("✅ Веб-аутентификация настроена")
        print("✅ Таблицы пользователей созданы")
        print("✅ Можно тестировать регистрацию")
    else:
        print("\n❌ Ошибка настройки базы данных")

if __name__ == "__main__":
    main() 