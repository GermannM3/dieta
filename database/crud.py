from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import DBAPIError, DisconnectionError, InterfaceError
from database.init_database import engine, User, async_session
import asyncio
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_db_connection(max_retries=3, delay=1):
    """Декоратор для повторных попыток подключения к БД"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (DBAPIError, DisconnectionError, InterfaceError, ConnectionResetError, OSError) as e:
                    logger.warning(f"Попытка {attempt + 1}/{max_retries} - Ошибка БД в {func.__name__}: {e}")
                    if attempt == max_retries - 1:
                        logger.error(f"Все попытки исчерпаны для {func.__name__}")
                        raise
                    await asyncio.sleep(delay * (attempt + 1))
                except Exception as e:
                    logger.error(f"Неожиданная ошибка в {func.__name__}: {e}")
                    raise
            return None
        return wrapper
    return decorator

async def get_db_session():
    """Получает сессию базы данных с обработкой ошибок"""
    try:
        async with async_session() as session:
            yield session
    except (DBAPIError, DisconnectionError, InterfaceError) as e:
        logger.error(f"Ошибка соединения с базой данных: {e}")
        # Попытка переподключения
        await asyncio.sleep(1)
        async with async_session() as session:
            yield session

@retry_db_connection()
async def add_user_if_not_exists(tg_id: int):
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if user is None:
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()

@retry_db_connection()
async def get_user_profile(tg_id: int):
    """Получает профиль пользователя"""
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if user:
            return {
                'name': user.name,
                'age': user.age,
                'gender': user.gender,
                'weight': user.weight,
                'height': user.height,
                'activity_level': user.activity_level,
                'water_ml': user.water_ml,
                'score': user.score,
                'streak_days': user.streak_days
            }
    return None

@retry_db_connection()
async def update_user_profile(tg_id: int, profile_data: dict):
    """Обновляет профиль пользователя"""
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if user:
            for key, value in profile_data.items():
                if hasattr(user, key) and value is not None:
                    setattr(user, key, value)
            await session.commit()
            return True
    return False

@retry_db_connection()
async def get_context(tg_id: int):
    async with async_session() as session:
        user = await session.get(User, tg_id)
        return user.chat_context if user else None

@retry_db_connection()
async def add_to_context(tg_id: int, message: str):
    """Добавляет сообщение в контекст пользователя"""
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if user:
            context = user.chat_context or []
            context.append(message)
            # Ограничиваем контекст 50 сообщениями
            if len(context) > 50:
                context = context[-50:]
            user.chat_context = context
            await session.commit()

@retry_db_connection()
async def update_context(tg_id: int, context: list):
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if user:
            context = context if len(context) <= 50 else context[2:]
            user.chat_context = context
            await session.commit()

@retry_db_connection()
async def reset_context(tg_id: int):
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if user:
            user.chat_context = None
            await session.commit()

@retry_db_connection()
async def save_fsm_state(tg_id: int, state: str, data: dict = None):
    """Сохраняет состояние FSM пользователя"""
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if user:
            user.fsm_state = state
            user.fsm_data = data or {}
            await session.commit()

@retry_db_connection()
async def get_fsm_state(tg_id: int):
    """Получает состояние FSM пользователя"""
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if user:
            return user.fsm_state, user.fsm_data or {}
    return None, {}

@retry_db_connection()
async def clear_fsm_state(tg_id: int):
    """Очищает состояние FSM пользователя"""
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if user:
            user.fsm_state = None
            user.fsm_data = None
            await session.commit()

@retry_db_connection()
async def amount_of_users():
    async with async_session() as session:
        amount = await session.scalar(func.count(User.tg_id))
        return amount

@retry_db_connection()
async def get_all_users():
    async with async_session() as session:
        users = await session.execute(select(User.tg_id))
        users = users.scalars().all()
        return users 