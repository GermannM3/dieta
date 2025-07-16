from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import BigInteger, JSON, Float, String, Integer, ForeignKey, Column, DateTime, text
from dotenv import load_dotenv
from sqlalchemy.orm import relationship
import os
import psycopg2
import csv
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    
    tg_id = mapped_column(BigInteger, primary_key=True)
    chat_context: Mapped[list] = mapped_column(JSON, nullable=True)
    # Новые поля профиля
    name: Mapped[str] = mapped_column(String, nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    gender: Mapped[str] = mapped_column(String, nullable=True)
    weight: Mapped[float] = mapped_column(Float, nullable=True)
    height: Mapped[float] = mapped_column(Float, nullable=True)
    activity_level: Mapped[int] = mapped_column(Integer, nullable=True)
    water_ml: Mapped[int] = mapped_column(Integer, nullable=True)  # трекер воды
    # Поля для баллов и стрика
    score: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, nullable=True, default=0)
    # Поле для сохранения состояния FSM
    fsm_state: Mapped[str] = mapped_column(String, nullable=True)
    fsm_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    # Связи
    meals = relationship('Meal', back_populates='user')
    presets = relationship('Preset', back_populates='user')

class Meal(Base):
    __tablename__ = "meals"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=False)
    food_name = Column(String, nullable=False)
    food_name_en = Column(String, nullable=True)  # Название на английском
    weight_grams = Column(Float, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=True, default=0)  # Белки
    fat = Column(Float, nullable=True, default=0)      # Жиры
    carbs = Column(Float, nullable=True, default=0)    # Углеводы
    fiber = Column(Float, nullable=True, default=0)    # Клетчатка
    sugar = Column(Float, nullable=True, default=0)    # Сахар
    sodium = Column(Float, nullable=True, default=0)   # Натрий
    date = Column(String, nullable=False)
    time = Column(String, nullable=False)
    meal_type = Column(String, nullable=True, default='other')  # breakfast, lunch, dinner, snack, other
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='meals')

class Preset(Base):
    __tablename__ = 'presets'
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(BigInteger, ForeignKey('users.tg_id'))
    name = mapped_column(String)
    food_items = mapped_column(JSON)  # [{food_name, weight, ...}]
    user = relationship('User', back_populates='presets')

class DailyStats(Base):
    __tablename__ = 'daily_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=False)
    date = Column(String, nullable=False)  # YYYY-MM-DD
    total_calories = Column(Float, default=0)
    total_meals = Column(Integer, default=0)
    water_ml = Column(Integer, default=0)
    mood_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class FatTracking(Base):
    __tablename__ = 'fat_tracking'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=False)
    waist_cm = Column(Float, nullable=False)  # Обхват талии в см
    hip_cm = Column(Float, nullable=False)    # Обхват бедер в см
    neck_cm = Column(Float, nullable=True)    # Обхват шеи в см (для мужчин)
    gender = Column(String, nullable=False)   # 'male' или 'female'
    body_fat_percent = Column(Float, nullable=False)  # Рассчитанный процент жира
    goal_fat_percent = Column(Float, nullable=True)   # Целевой процент жира
    recommendation = Column(String, nullable=True)    # Рекомендация от Mistral AI
    date = Column(String, nullable=False)     # YYYY-MM-DD
    created_at = Column(DateTime, default=datetime.utcnow)

class Food(Base):
    __tablename__ = 'food'
    fdc_id = mapped_column(BigInteger, primary_key=True)
    description = mapped_column(String)
    food_category_id = mapped_column(String, nullable=True)
    data_type = mapped_column(String, nullable=True)

class FoodNutrient(Base):
    __tablename__ = 'food_nutrient'
    id = mapped_column(BigInteger, primary_key=True)
    fdc_id = mapped_column(BigInteger)
    nutrient_id = mapped_column(BigInteger)
    amount = mapped_column(Float)

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL не задан в .env!')

# Исправляем схему подключения для asyncpg
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://', 1)
# Удаляем ?sslmode=require для asyncpg
if '?sslmode=require' in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace('?sslmode=require', '')

# Используем asyncpg для асинхронного подключения к PostgreSQL
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    future=True,
    pool_size=5,  # Уменьшаем размер пула для быстрого старта
    max_overflow=10,  # Уменьшаем максимальное количество дополнительных соединений
    pool_pre_ping=True,  # Проверяем соединения перед использованием
    pool_recycle=1800,  # Пересоздаем соединения каждые 30 минут
    pool_timeout=10,  # Уменьшаем таймаут получения соединения из пула
    connect_args={
        "server_settings": {
            "application_name": "diet_bot"
        },
        "command_timeout": 10   # Таймаут выполнения команд
    }
)
async_session = async_sessionmaker(
    engine, 
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

default_metadata = Base.metadata

async def init_db():
    """Инициализация базы данных с оптимизированными настройками"""
    try:
        async with engine.begin() as conn:
            # Проверяем, существуют ли таблицы
            result = await conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                );
            """))
            tables_exist = result.scalar()
            
            if not tables_exist:
                print("Создание таблиц базы данных...")
                await conn.run_sync(Base.metadata.create_all)
                print("Таблицы созданы успешно")
            else:
                print("Таблицы уже существуют")
    except Exception as e:
        print(f"Ошибка инициализации базы данных: {e}")
        # Создаем таблицы в любом случае
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

def import_food_csv():
    import os
    db_url = os.getenv('DATABASE_URL')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    with open('fooddata_tmp/FoodData_Central_csv_2025-04-24/food.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            batch.append((int(row['fdc_id']), row['description'], row.get('food_category_id'), row.get('data_type')))
            if len(batch) >= 10000:
                cur.executemany('INSERT INTO food (fdc_id, description, food_category_id, data_type) VALUES (%s, %s, %s, %s) ON CONFLICT (fdc_id) DO NOTHING', batch)
                batch = []
        if batch:
            cur.executemany('INSERT INTO food (fdc_id, description, food_category_id, data_type) VALUES (%s, %s, %s, %s) ON CONFLICT (fdc_id) DO NOTHING', batch)
    conn.commit()
    cur.close()
    conn.close()

def import_food_nutrient_csv():
    import os
    db_url = os.getenv('DATABASE_URL')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    with open('fooddata_tmp/FoodData_Central_csv_2025-04-24/food_nutrient.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        batch = []
        for row in reader:
            try:
                batch.append((int(row['id']), int(row['fdc_id']), int(row['nutrient_id']), float(row['amount'])))
            except Exception:
                continue
            if len(batch) >= 10000:
                cur.executemany('INSERT INTO food_nutrient (id, fdc_id, nutrient_id, amount) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING', batch)
                batch = []
        if batch:
            cur.executemany('INSERT INTO food_nutrient (id, fdc_id, nutrient_id, amount) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING', batch)
    conn.commit()
    cur.close()
    conn.close()


