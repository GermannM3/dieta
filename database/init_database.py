from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import BigInteger, JSON, Float, String, Integer, ForeignKey, Column, DateTime, text, Boolean
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
    # Поля для жировой массы (синхронизация с FatTracking)
    body_fat_percent: Mapped[float] = mapped_column(Float, nullable=True)  # Текущий процент жира
    goal_fat_percent: Mapped[float] = mapped_column(Float, nullable=True)  # Целевой процент жира
    # Поле для премиум-подписки
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
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

class Subscription(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.tg_id'), nullable=False)
    subscription_type = Column(String, nullable=False)  # 'diet_consultant' или 'menu_generator'
    payment_id = Column(String, nullable=False)  # ID платежа в YooMoney
    amount = Column(Float, nullable=False)  # Сумма платежа
    currency = Column(String, default='RUB')
    status = Column(String, default='pending')  # pending, completed, failed, refunded
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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

class WebUser(Base):
    """Модель пользователей веб-приложения (замена Supabase)"""
    __tablename__ = 'web_users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    is_confirmed = Column(Boolean, default=False)
    confirmation_code = Column(String(10))
    reset_code = Column(String(10))
    reset_code_expires = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WebProfile(Base):
    """Профили для веб-пользователей (замена Supabase profiles)"""
    __tablename__ = 'web_profiles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('web_users.id'), nullable=False)
    name = Column(String(100))
    gender = Column(String(10))  # 'male', 'female'
    age = Column(Integer)
    weight = Column(Float)
    height = Column(Float)
    activity_level = Column(Float)
    daily_target = Column(Float)
    water_target = Column(Integer, default=2000)
    steps_target = Column(Integer, default=10000)
    mood = Column(String(20))  # 'excellent', 'good', 'okay', 'bad', 'terrible'
    water_ml = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    score = Column(Integer, default=0)
    is_premium = Column(Boolean, default=False)  # Поле для премиум-подписки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WebMeal(Base):
    """Приемы пищи для веб-пользователей (замена Supabase meals)"""
    __tablename__ = 'web_meals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('web_users.id'), nullable=False)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    time = Column(String(8))  # HH:MM:SS
    food_name = Column(String(200), nullable=False)
    weight_grams = Column(Float, nullable=False)
    calories = Column(Float, nullable=False)
    protein = Column(Float, default=0)
    fat = Column(Float, default=0)
    carbs = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class WebPreset(Base):
    """Шаблоны питания для веб-пользователей (замена Supabase presets)"""
    __tablename__ = 'web_presets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('web_users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    meal_type = Column(String(20))  # 'breakfast', 'lunch', 'dinner', 'snack'
    food_items = Column(JSON)  # Список продуктов
    total_calories = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    pool_size=10,  # Увеличиваем размер пула
    max_overflow=20,  # Увеличиваем максимальное количество дополнительных соединений
    pool_pre_ping=True,  # Проверяем соединения перед использованием
    pool_recycle=3600,  # Пересоздаем соединения каждые 60 минут
    pool_timeout=30,  # Увеличиваем таймаут получения соединения из пула
    connect_args={
        "server_settings": {
            "application_name": "diet_bot"
        },
        "command_timeout": 30   # Увеличиваем таймаут выполнения команд
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


