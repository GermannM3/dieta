import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://neondb_owner:npg_wNt53iaxXIBq@ep-lively-hall-aduj1169-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require')

# Создаем асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Установите True для отладки SQL запросов
    pool_pre_ping=True,
    pool_recycle=300,
)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Базовый класс для моделей
Base = declarative_base()

class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    @staticmethod
    async def get_session() -> AsyncSession:
        """Получает сессию базы данных"""
        async with async_session_maker() as session:
            return session
    
    @staticmethod
    async def test_connection() -> bool:
        """Тестирует подключение к базе данных"""
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                await result.fetchone()
                return True
        except Exception as e:
            print(f"Ошибка подключения к БД: {e}")
            return False
    
    @staticmethod
    async def create_tables():
        """Создает все таблицы"""
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                print("Таблицы успешно созданы")
        except Exception as e:
            print(f"Ошибка создания таблиц: {e}")
    
    @staticmethod
    async def drop_tables():
        """Удаляет все таблицы"""
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                print("Таблицы успешно удалены")
        except Exception as e:
            print(f"Ошибка удаления таблиц: {e}")
    
    @staticmethod
    async def execute_query(query: str, params: dict = None):
        """Выполняет SQL запрос"""
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text(query), params or {})
                return result
        except Exception as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None

# Функция для получения сессии (для обратной совместимости)
async def get_db_session() -> AsyncSession:
    """Получает сессию базы данных (для обратной совместимости)"""
    return await DatabaseManager.get_session()

# Функция для тестирования подключения
async def test_db_connection() -> bool:
    """Тестирует подключение к базе данных (для обратной совместимости)"""
    return await DatabaseManager.test_connection()

if __name__ == "__main__":
    # Тестирование подключения
    async def test():
        print("Тестирование подключения к базе данных...")
        if await test_db_connection():
            print("✅ Подключение к БД успешно!")
        else:
            print("❌ Ошибка подключения к БД!")
    
    asyncio.run(test()) 