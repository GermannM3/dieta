#!/bin/bash
echo "🚨 ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ СЕРВЕРА"
echo "=================================="

cd /opt/dieta || { echo "❌ Папка не найдена!"; exit 1; }

# Останавливаем все контейнеры
echo "🛑 Остановка всех контейнеров..."
docker-compose down 2>/dev/null || true
docker stop $(docker ps -q) 2>/dev/null || true

echo "🔧 ИСПРАВЛЕНИЕ 1: DATABASE_URL"
echo "==============================="

# Проверяем .env
if [[ -f ".env" ]]; then
    echo "📋 Текущий .env:"
    grep "DATABASE_URL" .env
    
    # Проверяем есть ли шаблон
    if grep -q "user:password@host:port" .env; then
        echo "❌ НАЙДЕН ШАБЛОН! Исправляем..."
        
        # Заменяем на SQLite для быстрого запуска
        sed -i 's|DATABASE_URL=postgresql+asyncpg://user:password@host:port/database|DATABASE_URL=sqlite+aiosqlite:///./dieta.db|g' .env
        
        echo "✅ DATABASE_URL исправлен на SQLite"
        echo "📋 Новый DATABASE_URL:"
        grep "DATABASE_URL" .env
    else
        echo "✅ DATABASE_URL выглядит правильно"
    fi
else
    echo "❌ .env не найден! Создаем..."
    cat > .env << 'EOF'
TG_TOKEN=your_telegram_bot_token_from_botfather
ADMIN_ID=your_telegram_id_number
DATABASE_URL=sqlite+aiosqlite:///./dieta.db
GIGACHAT_CLIENT_ID=your_gigachat_client_id
GIGACHAT_AUTH_KEY=your_gigachat_auth_key
GIGACHAT_ACCESS_TOKEN=your_gigachat_access_token
MISTRAL_API_KEY=your_mistral_api_key
CALORIE_NINJAS_API_KEY=your_calorie_ninjas_api_key
LOG_LEVEL=INFO
API_PORT=8000
EOF
    echo "✅ .env создан с SQLite"
fi

echo ""
echo "🔧 ИСПРАВЛЕНИЕ 2: REQUIREMENTS"
echo "=============================="

# Добавляем aiosqlite в requirements.txt
if [[ -f "requirements.txt" ]]; then
    if ! grep -q "aiosqlite" requirements.txt; then
        echo "aiosqlite>=0.20.0" >> requirements.txt
        echo "✅ Добавлен aiosqlite в requirements.txt"
    else
        echo "✅ aiosqlite уже есть в requirements.txt"
    fi
else
    echo "❌ requirements.txt не найден!"
fi

echo ""
echo "🔧 ИСПРАВЛЕНИЕ 3: DATABASE INITIALIZATION"
echo "========================================="

# Исправляем init_database.py для правильной работы с SQLite
if [[ -f "database/init_database.py" ]]; then
    # Делаем резервную копию
    cp database/init_database.py database/init_database.py.backup
    
    # Исправляем код
    cat > database/init_database.py << 'EOF'
"""
Database initialization module
"""
import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, BigInteger, Boolean
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Base model
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = 'users'
    
    tg_id = Column(BigInteger, primary_key=True)
    chat_context = Column(Text, default="")
    name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(10))
    weight = Column(Float)
    height = Column(Float)
    activity_level = Column(String(50))
    water_ml = Column(Integer, default=0)
    score = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)

class Meal(Base):
    __tablename__ = 'meals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    date = Column(String(10))
    meal_type = Column(String(20))
    food_name = Column(String(200))
    quantity = Column(Float)
    calories = Column(Float)
    protein = Column(Float, default=0)
    fat = Column(Float, default=0)
    carbs = Column(Float, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Preset(Base):
    __tablename__ = 'presets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    name = Column(String(100))
    foods = Column(Text)

class Food(Base):
    __tablename__ = 'foods'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200))
    calories_per_100g = Column(Float)
    protein_per_100g = Column(Float, default=0)
    fat_per_100g = Column(Float, default=0)
    carbs_per_100g = Column(Float, default=0)

class FoodNutrient(Base):
    __tablename__ = 'food_nutrients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    food_id = Column(Integer)
    nutrient_name = Column(String(100))
    value_per_100g = Column(Float)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./dieta.db')

# Создаем engine
try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True
    )
    print(f"✅ Database engine created: {DATABASE_URL}")
except Exception as e:
    print(f"❌ Database engine error: {e}")
    raise

# Создаем session maker
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        raise

# For compatibility
def get_session():
    return async_session()
EOF
    
    echo "✅ database/init_database.py исправлен"
else
    echo "❌ database/init_database.py не найден!"
fi

echo ""
echo "🔧 ИСПРАВЛЕНИЕ 4: DOCKER REBUILD"
echo "================================"

# Полная очистка Docker
docker system prune -a -f

# Пересборка API контейнера
echo "🔨 Пересборка API контейнера..."
docker-compose build --no-cache api

if [ $? -eq 0 ]; then
    echo "✅ API контейнер собран"
else
    echo "❌ Ошибка сборки API контейнера"
    exit 1
fi

# Запуск API
echo "🚀 Запуск API..."
docker-compose up -d api

sleep 10

# Проверка API
echo "🔍 Проверка API..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API работает!"
else
    echo "⚠️ API еще не готов, проверяем логи..."
    docker-compose logs api
fi

echo ""
echo "✅ ЭКСТРЕННОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo "===================================="
echo ""
echo "🌐 Проверьте:"
echo "- API: http://5.129.198.80:8000/health"
echo "- Логи: docker-compose logs -f api"
echo ""
echo "📝 Следующие шаги:"
echo "1. Если API работает, запустите bot: docker-compose up -d bot"
echo "2. Потом запустите frontend: docker-compose up -d frontend"
echo "3. Настройте правильный PostgreSQL URL в .env если нужно" 