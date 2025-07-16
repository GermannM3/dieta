from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import DBAPIError, DisconnectionError
from database.init_database import engine, User, async_session
import asyncio
import logging

logger = logging.getLogger(__name__)

async def get_db_session():
    """Получает сессию базы данных с обработкой ошибок"""
    try:
        async with async_session() as session:
            yield session
    except (DBAPIError, DisconnectionError) as e:
        logger.error(f"Ошибка соединения с базой данных: {e}")
        # Попытка переподключения
        await asyncio.sleep(1)
        async with async_session() as session:
            yield session

async def add_user_if_not_exists(tg_id: int):
    try:
        async with async_session() as session:
            user = await session.get(User, tg_id)
            if user is None:
                user = User(tg_id=tg_id)
                session.add(user)
                await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя {tg_id}: {e}")
        raise

async def get_user_profile(tg_id: int):
    """Получает профиль пользователя"""
    try:
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
    except Exception as e:
        logger.error(f"Ошибка при получении профиля пользователя {tg_id}: {e}")
        return None

async def update_user_profile(tg_id: int, profile_data: dict):
    """Обновляет профиль пользователя"""
    try:
        async with async_session() as session:
            user = await session.get(User, tg_id)
            if user:
                for key, value in profile_data.items():
                    if hasattr(user, key) and value is not None:
                        setattr(user, key, value)
                await session.commit()
                return True
            return False
    except Exception as e:
        logger.error(f"Ошибка при обновлении профиля пользователя {tg_id}: {e}")
        return False

async def get_context(tg_id: int):
    try:
        async with async_session() as session:
            user = await session.get(User, tg_id)
            return user.chat_context if user else None
    except Exception as e:
        logger.error(f"Ошибка при получении контекста пользователя {tg_id}: {e}")
        return None

async def add_to_context(tg_id: int, message: str):
    """Добавляет сообщение в контекст пользователя"""
    try:
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
    except Exception as e:
        logger.error(f"Ошибка при добавлении в контекст пользователя {tg_id}: {e}")

async def update_context(tg_id: int, context: list):
    try:
        async with async_session() as session:
            user = await session.get(User, tg_id)
            if user:
                context = context if len(context) <= 50 else context[2:]
                user.chat_context = context
                await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при обновлении контекста пользователя {tg_id}: {e}")

async def reset_context(tg_id: int):
    try:
        async with async_session() as session:
            user = await session.get(User, tg_id)
            if user:
                user.chat_context = None
                await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при сбросе контекста пользователя {tg_id}: {e}")

async def save_fsm_state(tg_id: int, state: str, data: dict = None):
    """Сохраняет состояние FSM пользователя"""
    try:
        async with async_session() as session:
            user = await session.get(User, tg_id)
            if user:
                user.fsm_state = state
                user.fsm_data = data or {}
                await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при сохранении FSM состояния пользователя {tg_id}: {e}")

async def get_fsm_state(tg_id: int):
    """Получает состояние FSM пользователя"""
    try:
        async with async_session() as session:
            user = await session.get(User, tg_id)
            if user:
                return user.fsm_state, user.fsm_data or {}
            return None, {}
    except Exception as e:
        logger.error(f"Ошибка при получении FSM состояния пользователя {tg_id}: {e}")
        return None, {}

async def clear_fsm_state(tg_id: int):
    """Очищает состояние FSM пользователя"""
    try:
        async with async_session() as session:
            user = await session.get(User, tg_id)
            if user:
                user.fsm_state = None
                user.fsm_data = None
                await session.commit()
    except Exception as e:
        logger.error(f"Ошибка при очистке FSM состояния пользователя {tg_id}: {e}")

async def amount_of_users():
    try:
        async with async_session() as session:
            amount = await session.scalar(func.count(User.tg_id))
            return amount
    except Exception as e:
        logger.error(f"Ошибка при подсчете пользователей: {e}")
        return 0

async def get_all_users_id():
    try:
        async with async_session() as session:
            users = await session.execute(select(User.tg_id))
            users = users.scalars().all()
            return users
    except Exception as e:
        logger.error(f"Ошибка при получении списка пользователей: {e}")
        return []