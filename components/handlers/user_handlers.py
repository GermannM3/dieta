from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ContentType, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
import os
import requests
import json
from datetime import datetime, timedelta
import asyncio
import logging

from database.crud import add_user_if_not_exists, reset_context, add_to_context, save_fsm_state, get_fsm_state, clear_fsm_state, get_user_profile
import components.keyboards.user_kb as kb
from components.states.user_states import Chat, Image
from api.ai_api.generate_text import translate
from api.ai_api.gigachat_api import generate_text_gigachat
from components.keyboards.user_kb import main_menu_kb

# --- Импортируем async_session ---
from database.init_database import async_session, User, Meal, Preset

# Константы для таймаутов
REQUEST_TIMEOUT = 30  # Увеличенный таймаут для всех запросов
CONNECTION_TIMEOUT = 10  # Таймаут подключения

# API URL для обращения к серверу
API_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

router = Router()

# Системный промпт для диетолога
DIETOLOG_PROMPT = """
Ты профессиональный диетолог с 15-летним опытом работы. Твоя специализация - персональное консультирование по питанию, составление диет и планов питания.

Твои основные принципы:
1. Научный подход - все рекомендации основаны на доказательной медицине
2. Персонализация - учитываешь индивидуальные особенности каждого клиента
3. Безопасность - не рекомендуешь экстремальные диеты или опасные практики
4. Устойчивость - помогаешь формировать здоровые привычки на всю жизнь
5. Поддержка - мотивируешь и поддерживаешь клиентов

Ты умеешь:
- Анализировать рацион и давать рекомендации по улучшению
- Рассчитывать индивидуальную потребность в калориях и БЖУ
- Составлять персональные планы питания
- Давать советы по снижению/набору веса
- Рекомендовать продукты и их сочетания
- Объяснять принципы здорового питания
- Помогать с мотивацией и преодолением трудностей

Всегда будь дружелюбным, профессиональным и поддерживающим. Давай конкретные, практичные советы.
"""

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    # Автоматически регистрируем пользователя
    await add_user_if_not_exists(tg_id=message.from_user.id)
    
    # Восстанавливаем состояние FSM если есть
    saved_state, saved_data = await get_fsm_state(message.from_user.id)
    if saved_state:
        await state.set_state(saved_state)
        if saved_data:
            await state.set_data(saved_data)
    
    # Простая проверка профиля без зависимости от API
    try:
        # Получаем профиль пользователя напрямую из БД
        profile = await get_user_profile(message.from_user.id)
        if not profile or not profile.get('name'):
            # Профиль не заполнен, но не создаем его автоматически
            # Пользователь сам заполнит через /profile
            pass
    except Exception as e:
        # Если ошибка - продолжаем без профиля
        print(f"Ошибка получения профиля: {e}")
    
    await message.answer(
        f'<b>🎉 Привет, {message.from_user.first_name}!</b>\n'
        f'Я — ваш персональный диетолог и помощник по здоровому питанию! 🥗\n\n'
        
        f'<b>🤖 Что я умею:</b>\n'
        f'🍎 Анализирую калории и БЖУ любых продуктов с помощью ИИ\n'
        f'📊 Веду статистику питания и отслеживаю прогресс\n'
        f'🥘 Генерирую персональные меню под ваши цели\n'
        f'👨‍⚕️ Консультирую как профессиональный диетолог\n'
        f'💧 Отслеживаю потребление воды\n'
        f'📸 Распознаю еду на фотографиях\n'
        f'📝 Создаю шаблоны для быстрого добавления блюд\n'
        f'🏆 Мотивирую системой баллов и достижений\n\n'
        
        f'<b>🎯 Мои возможности:</b>\n'
        f'• Точный подсчет калорий с помощью нейросети GigaChat\n'
        f'• Персональные рекомендации на основе вашего профиля\n'
        f'• Интеллектуальный анализ пищевых привычек\n'
        f'• Поддержка целей: похудение, набор массы, поддержание\n\n'
        
        f'<b>🚀 Быстрый старт:</b>\n'
        f'1️⃣ Создайте профиль: /profile 👤\n'
        f'2️⃣ Добавьте первый прием пищи: /addmeal 🍽️\n'
        f'3️⃣ Получите персональное меню: /menu 📋\n'
        f'4️⃣ Задайте вопрос диетологу: /dietolog 👨‍⚕️\n\n'
        
        f'<b>📱 Основные команды:</b>\n'
        f'/profile — Управление профилем\n'
        f'/addmeal — Добавить еду\n'
        f'/history — История питания\n'
        f'/menu — Сгенерировать меню\n'
        f'/dietolog — Консультация диетолога\n'
        f'/water — Трекер воды\n'
        f'/score — Прогресс и достижения\n'
        f'/presets — Мои шаблоны\n\n'
        
        f'<b>💡 Рекомендация:</b>\n'
        f'<i>Начните с создания профиля, чтобы получать персональные рекомендации!</i>\n\n'
        
        f'Выберите действие из меню ниже ⬇️',
        reply_markup=main_menu_kb
    )

@router.callback_query(F.data == 'start_dialog')
async def start_dialog(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'Chat:active':
        await callback.answer('Диалог уже начат')
        await callback.message.answer('<b>Диалог уже активен</b>')
    else:
        await callback.message.answer('<b>Диалог успешно начат. Для завершения используйте /stop</b>')
        await callback.answer('Диалог начат')
        await state.set_state(Chat.active)
        # Сохраняем состояние
        await save_fsm_state(callback.from_user.id, 'Chat:active')

@router.message(Command('stop'))
async def stop(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'Chat:active':
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer('<b>Консультация завершена. Для новой консультации используйте /dietolog</b>')
        await reset_context(tg_id=message.from_user.id)
    elif current_state == 'Chat:waiting':
        await message.answer('<b>Дождитесь ответа, чтобы закончить консультацию</b>')
    else:
        await message.answer('<b>Нет активной консультации. Чтобы начать консультацию используйте /dietolog</b>')

@router.message(Command('reset'))
async def reset(message: Message, state: FSMContext):
    await reset_context(tg_id=message.from_user.id)
    await clear_fsm_state(message.from_user.id)
    await state.clear()
    await message.answer('<b>История консультаций очищена</b>')

@router.message(Command('generate'))
async def generate_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == 'Chat:active' or current_state == 'Chat:waiting':
        await message.answer('<b>Диалог уже активен</b>')
    else:
        await message.answer('<b>Диалог успешно начат. Для завершения используйте /stop</b>')
        await state.set_state(Chat.active)
        await save_fsm_state(message.from_user.id, 'Chat:active')

@router.message(Command('info'))
async def info(message: Message):
    await message.answer('🚫 <b><i>Правила:</i></b>\n• Запрещён контент с ненавистью, дискриминацией (раса, пол, религия и др.), оскорблениями групп/личностей.\n• Нельзя использовать для буллинга, угроз, ксенофобии, расизма или унижающих материалов.\nПользователь несет ответственность за свои запросы.\n\n<b>Бот создан в добросовестных целях — соблюдайте уважение! 🙌</b>')

@router.message(Chat.active)
async def chat_active(message: Message, state: FSMContext): 
    current_state = await state.get_state()
    if current_state == 'Chat:waiting':
        await message.answer('<b>Дождитесь ответа</b>')
    else:
        if message.content_type == ContentType.TEXT:
            waiting_message = await message.answer('<b><i>⏳ Диетолог анализирует ваш вопрос...</i></b>')
            await state.set_state(Chat.waiting)
            await save_fsm_state(message.from_user.id, 'Chat:waiting')
            
            # Получаем данные профиля пользователя
            try:
                r = requests.get(f'{API_URL}/api/profile?tg_id={message.from_user.id}', timeout=REQUEST_TIMEOUT)
                profile_data = {}
                if r.status_code == 200:
                    profile = r.json().get('profile', {})
                    if profile.get('name'):
                        profile_data = profile
            except:
                profile_data = {}
            
            # Формируем контекст с системным промптом диетолога и данными профиля
            profile_context = ""
            if profile_data:
                profile_context = f"""
Данные клиента:
- Имя: {profile_data.get('name', 'Не указано')}
- Возраст: {profile_data.get('age', 'Не указан')} лет
- Пол: {profile_data.get('gender', 'Не указан')}
- Вес: {profile_data.get('weight', 'Не указан')} кг
- Рост: {profile_data.get('height', 'Не указан')} см
- Уровень активности: {profile_data.get('activity_level', 'Не указан')}

"""
            
            full_prompt = f"{DIETOLOG_PROMPT}\n\n{profile_context}Клиент: {message.text}\n\nДиетолог:"
            
            # Используем GigaChat для ответа диетолога
            ai_response = await generate_text_gigachat(prompt=full_prompt)
            
            # Добавляем подпись с /stop
            ai_response += "\n\n💡 Если хотите завершить приём, нажмите /stop"
            
            # Сохраняем контекст для продолжения диалога
            await add_to_context(tg_id=message.from_user.id, message=f"Пользователь: {message.text}")
            await add_to_context(tg_id=message.from_user.id, message=f"Ассистент: {ai_response}")
            
            try:
                await message.answer(ai_response, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await message.answer(ai_response[:4050], parse_mode=None)
            await state.set_state(Chat.active)
            await save_fsm_state(message.from_user.id, 'Chat:active')
            await waiting_message.delete()
        elif message.content_type == ContentType.PHOTO:
            from components.payment_system.payment_operations import check_premium
            access = check_premium(tg_id=message.from_user.id)
            if not access:
                await message.answer('<b>Для обработки изображений необходимо приобрести премиум подписку /premium</b>')
                return
            waiting_message = await message.answer('<b><i>⏳ Ответ генерируется...</i></b>')
            await state.set_state(Chat.waiting)
            await save_fsm_state(message.from_user.id, 'Chat:waiting')
            ai_response = await answer_to_view_prompt(message=message)
            ai_response = await style_changer(latex_code=ai_response)
            try:
                await message.answer(ai_response, parse_mode=ParseMode.MARKDOWN)
            except TelegramBadRequest:
                await message.answer(ai_response[:4050], parse_mode=None)
            await state.set_state(Chat.active)
            await save_fsm_state(message.from_user.id, 'Chat:active')
            await waiting_message.delete()
        else: 
            await message.answer('<b>Поддерживаются только текстовые сообщения и изображения</b>')

@router.message(Chat.waiting)
async def waiting(message: Message):
    await message.answer('<b>Дождитесь ответа</b>')

@router.callback_query(F.data == 'back')
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(
        f'<b>🎉 Привет, {callback.from_user.first_name}!</b>\n'
        f'Я — ваш персональный диетолог и помощник по здоровому питанию! 🥗\n\n'
        
        f'<b>🤖 Что я умею:</b>\n'
        f'🍎 Анализирую калории и БЖУ любых продуктов с помощью ИИ\n'
        f'📊 Веду статистику питания и отслеживаю прогресс\n'
        f'🥘 Генерирую персональные меню под ваши цели\n'
        f'👨‍⚕️ Консультирую как профессиональный диетолог\n'
        f'💧 Отслеживаю потребление воды\n'
        f'📸 Распознаю еду на фотографиях\n'
        f'📝 Создаю шаблоны для быстрого добавления блюд\n'
        f'🏆 Мотивирую системой баллов и достижений\n\n'
        
        f'<b>🚀 Быстрый старт:</b>\n'
        f'1️⃣ Создайте профиль: /profile 👤\n'
        f'2️⃣ Добавьте первый прием пищи: /addmeal 🍽️\n'
        f'3️⃣ Получите персональное меню: /menu 📋\n'
        f'4️⃣ Задайте вопрос диетологу: /dietolog 👨‍⚕️\n\n'
        
        f'<b>💡 Рекомендация:</b>\n'
        f'<i>Начните с создания профиля, чтобы получать персональные рекомендации!</i>\n\n'
        
        f'Выберите действие из меню ниже ⬇️',
        reply_markup=kb.main_menu_kb
    )
    await state.clear()

class ProfileFSM(StatesGroup):
    name = State()
    age = State()
    gender = State()
    weight = State()
    height = State()
    activity = State()

class EditProfileFSM(StatesGroup):
    waiting = State()

@router.callback_query(F.data == 'profile')
async def profile_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    import requests
    user_id = callback.from_user.id
    
    # Получаем данные профиля
    try:
        r = requests.get(f'{API_URL}/api/profile?tg_id={user_id}')
        if r.status_code == 200:
            profile = r.json().get('profile')
            if not profile or not profile.get('name'):
                await callback.message.answer('<b>Профиль не заполнен. Давайте заполним!</b>\nВведите ваше имя:')
                await state.set_state(ProfileFSM.name)
                return
            
            # Получаем данные о воде
            water_r = requests.get(f'{API_URL}/api/water?user_id={user_id}')
            water_ml = 0
            if water_r.status_code == 200:
                water_data = water_r.json()
                water_ml = water_data.get('water_ml', 0)
            
            # Получаем данные о жире из профиля пользователя
            fat_info = ""
            try:
                from database.init_database import async_session, User
                from api.ai_api.fat_calculator import FatPercentageCalculator
                
                async with async_session() as session:
                    user = await session.get(User, user_id)
                    if user and user.body_fat_percent:
                        category = FatPercentageCalculator.get_fat_category(
                            user.body_fat_percent, 
                            user.gender or 'male'
                        )
                        fat_info = f'🏃‍♀️ % жира: {user.body_fat_percent}% {category["emoji"]}\n'
                        if user.goal_fat_percent:
                            diff = user.goal_fat_percent - user.body_fat_percent
                            if abs(diff) <= 1:
                                fat_info += f'🎯 Цель: достигнута!\n'
                            else:
                                fat_info += f'🎯 До цели: {abs(diff):.1f}%\n'
            except:
                pass  # Если ошибка - просто не показываем данные о жире
            
            # Уровни активности
            activity_levels = {
                1: "Минимальная активность",
                2: "Низкая активность", 
                3: "Умеренная активность",
                4: "Высокая активность",
                5: "Очень высокая активность"
            }
            
            await callback.message.edit_text(
                f'<b>📊 Ваш профиль:</b>\n\n'
                f'👤 Имя: {profile.get("name", "Не указано")}\n'
                f'🎂 Возраст: {profile.get("age", "Не указан")} лет\n'
                f'⚧ Пол: {profile.get("gender", "Не указан")}\n'
                f'⚖️ Вес: {profile.get("weight", "Не указан")} кг\n'
                f'📏 Рост: {profile.get("height", "Не указан")} см\n'
                f'🏃‍♂️ Активность: {activity_levels.get(profile.get("activity_level"), "Не указан")}\n'
                f'{fat_info}'
                f'💧 Вода сегодня: {water_ml} мл\n'
                f'🏆 Баллы: {profile.get("score", 0)}\n'
                f'🔥 Дней подряд: {profile.get("streak_days", 0)}\n\n'
                f'<b>Выберите действие:</b>',
                reply_markup=kb.profile_kb
            )
        else:
            await callback.message.answer('<b>Ошибка получения профиля</b>')
    except Exception as e:
        error_msg = str(e).replace('<', '&lt;').replace('>', '&gt;')
        await callback.message.answer(f'<b>Ошибка соединения с сервером: {error_msg}</b>')

@router.message(ProfileFSM.name)
async def profile_name(message: Message, state: FSMContext):
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Создание профиля отменено", reply_markup=kb.main_menu_kb)
        return
    
    await state.update_data(name=message.text.strip())
    await message.answer('<b>Введите ваш возраст (число):</b>', reply_markup=kb.back_kb)
    await state.set_state(ProfileFSM.age)

@router.message(ProfileFSM.age)
async def profile_age(message: Message, state: FSMContext):
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Создание профиля отменено", reply_markup=kb.main_menu_kb)
        return
    
    try:
        age = int(message.text.strip())
        if not (5 < age < 120): raise ValueError
    except:
        await message.answer('<b>Возраст должен быть числом от 6 до 119</b>', reply_markup=kb.back_kb)
        return
    await state.update_data(age=age)
    await message.answer('<b>Ваш пол? (м/ж):</b>', reply_markup=kb.back_kb)
    await state.set_state(ProfileFSM.gender)

@router.message(ProfileFSM.gender)
async def profile_gender(message: Message, state: FSMContext):
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Создание профиля отменено", reply_markup=kb.main_menu_kb)
        return
    
    gender = message.text.strip().lower()
    if gender not in ['м', 'ж']:
        await message.answer('<b>Введите "м" или "ж"</b>', reply_markup=kb.back_kb)
        return
    await state.update_data(gender=gender)
    await message.answer('<b>Ваш вес (кг):</b>', reply_markup=kb.back_kb)
    await state.set_state(ProfileFSM.weight)

@router.message(ProfileFSM.weight)
async def profile_weight(message: Message, state: FSMContext):
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Создание профиля отменено", reply_markup=kb.main_menu_kb)
        return
    
    try:
        weight = float(message.text.strip())
        if not (20 < weight < 400): raise ValueError
    except:
        await message.answer('<b>Вес должен быть числом (20-400)</b>', reply_markup=kb.back_kb)
        return
    await state.update_data(weight=weight)
    await message.answer('<b>Ваш рост (см):</b>', reply_markup=kb.back_kb)
    await state.set_state(ProfileFSM.height)

@router.message(ProfileFSM.height)
async def profile_height(message: Message, state: FSMContext):
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Создание профиля отменено", reply_markup=kb.main_menu_kb)
        return
    
    try:
        height = float(message.text.strip())
        if not (80 < height < 250): raise ValueError
    except:
        await message.answer('<b>Рост должен быть числом (80-250)</b>', reply_markup=kb.back_kb)
        return
    await state.update_data(height=height)
    await message.answer('<b>Уровень активности (1-5):\n1 — минимум, 5 — максимум</b>', reply_markup=kb.back_kb)
    await state.set_state(ProfileFSM.activity)

@router.message(ProfileFSM.activity)
async def profile_activity(message: Message, state: FSMContext):
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Создание профиля отменено", reply_markup=kb.main_menu_kb)
        return
    
    try:
        activity = int(message.text.strip())
        if not (1 <= activity <= 5): raise ValueError
    except:
        await message.answer('<b>Введите число от 1 до 5</b>', reply_markup=kb.back_kb)
        return
    await state.update_data(activity=activity)
    data = await state.get_data()
    # Отправляем профиль на backend
    import requests
    payload = {
        'tg_id': message.from_user.id,
        'name': data['name'],
        'age': data['age'],
        'gender': data['gender'],
        'weight': data['weight'],
        'height': data['height'],
        'activity_level': data['activity']
    }
    try:
        r = requests.post(f'{API_URL}/api/profile', json=payload, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            await message.answer('<b>✅ Профиль сохранён!</b>', reply_markup=kb.main_menu_kb)
        else:
            error_detail = r.json().get('detail', 'Неизвестная ошибка') if r.status_code != 500 else 'Ошибка сервера'
            await message.answer(f'<b>❌ Ошибка сохранения профиля: {error_detail}</b>')
    except requests.exceptions.RequestException as e:
        await message.answer(f'<b>❌ Ошибка соединения с API сервером. Проверьте, что сервер запущен.</b>')
    except Exception as e:
        error_msg = str(e).replace('<', '&lt;').replace('>', '&gt;')
        await message.answer(f'<b>❌ Ошибка: {error_msg}</b>')
    await state.clear()

@router.callback_query(F.data == 'edit_profile')
async def edit_profile_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('<b>Давайте обновим ваш профиль!</b>\nВведите ваше имя:')
    await state.set_state(ProfileFSM.name)
    await save_fsm_state(callback.from_user.id, 'ProfileFSM:name')

@router.message(EditProfileFSM.waiting)
async def edit_profile_waiting(message: Message, state: FSMContext):
    """Обработка ввода данных для редактирования профиля"""
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Редактирование отменено", reply_markup=kb.main_menu_kb)
        return
    
    try:
        parts = message.text.strip().split('|')
        if len(parts) != 6:
            await message.answer(
                "❌ Неверный формат. Используйте:\n"
                "<code>имя|возраст|пол|вес|рост|активность</code>"
            )
            return
        
        name, age_str, gender, weight_str, height_str, activity_str = parts
        
        # Валидация данных
        try:
            age = int(age_str)
            if not (5 < age < 120):
                raise ValueError("Возраст должен быть от 6 до 119")
        except:
            await message.answer("❌ Неверный возраст")
            return
        
        if gender.lower() not in ['м', 'ж']:
            await message.answer("❌ Пол должен быть 'м' или 'ж'")
            return
        
        try:
            weight = float(weight_str)
            if not (20 < weight < 400):
                raise ValueError("Вес должен быть от 20 до 400 кг")
        except:
            await message.answer("❌ Неверный вес")
            return
        
        try:
            height = float(height_str)
            if not (80 < height < 250):
                raise ValueError("Рост должен быть от 80 до 250 см")
        except:
            await message.answer("❌ Неверный рост")
            return
        
        try:
            activity = int(activity_str)
            if not (1 <= activity <= 5):
                raise ValueError("Активность должна быть от 1 до 5")
        except:
            await message.answer("❌ Неверный уровень активности")
            return
        
        # Отправляем обновленные данные на API
        profile_data = {
            'name': name,
            'age': age,
            'gender': gender.lower(),
            'weight': weight,
            'height': height,
            'activity_level': activity
        }
        
        r = requests.put(f'{API_URL}/api/profile', params={'tg_id': message.from_user.id}, json=profile_data, timeout=10)
        
        if r.status_code == 200:
            await message.answer(
                "✅ <b>Профиль успешно обновлен!</b>\n\n"
                f"👤 Имя: {name}\n"
                f"🎂 Возраст: {age} лет\n"
                f"⚧ Пол: {gender}\n"
                f"⚖️ Вес: {weight} кг\n"
                f"📏 Рост: {height} см\n"
                f"🏃‍♂️ Активность: {activity}/5",
                reply_markup=kb.main_menu_kb
            )
        else:
            error_detail = r.json().get('detail', 'Неизвестная ошибка') if r.content else 'Ошибка сервера'
            await message.answer(f"❌ Ошибка обновления профиля: {error_detail}")
    
    except requests.exceptions.RequestException as e:
        await message.answer("❌ Ошибка соединения с API сервером")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    
    await state.clear()
    await clear_fsm_state(message.from_user.id)

# --- FSM группы для пользовательских сценариев ---
class AddMealFSM(StatesGroup):
    waiting = State()

class PresetFSM(StatesGroup):
    name = State()
    food = State()

class SimplePresetFSM(StatesGroup):
    waiting = State()

class WaterFSM(StatesGroup):
    add = State()

# --- Добавление еды ---
@router.message(Command('addmeal'))
@router.message(lambda message: message.text == 'Добавить еду')
async def addmeal_command(message: Message, state: FSMContext):
    # Устанавливаем состояние для добавления еды
    await state.set_state(AddMealFSM.waiting)
    
    message_text = (
        "🍽️ <b>Добавление еды</b>\n\n"
        "📝 Введите название блюда и вес в граммах\n"
        "💡 <i>Пример: Яблоко 150</i>\n\n"
        "Или выберите готовый шаблон ниже 👇"
    )
    
    await message.answer(message_text, reply_markup=kb.add_food_kb, parse_mode='HTML')
    await save_fsm_state(message.from_user.id, 'AddMealFSM:waiting')

@router.message(AddMealFSM.waiting)
async def addmeal_waiting(message: Message, state: FSMContext):
    if message.text.lower() == 'назад':
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Действие отменено", reply_markup=kb.main_menu_kb)
        return
        
    parts = message.text.strip().rsplit(' ', 1)
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Формат: название и вес в граммах.\nПример: Яблоко 150")
        return
    food_name, weight = parts[0], float(parts[1])
    
    # Получаем текущее время и дату
    now = datetime.now()
    date = now.strftime('%Y-%m-%d')
    time = now.strftime('%H:%M')
    
    # Используем GigaChat для анализа калорий с жестким промптом
    prompt = f"""
КРИТИЧЕСКИ ВАЖНО: Ты эксперт-диетолог с 20-летним опытом. Анализируй ТОЛЬКО реальную пищевую ценность продуктов. НЕ ФАНТАЗИРУЙ И НЕ ЗАВЫШАЙ калории!

ЗАДАЧА: Рассчитай точную пищевую ценность для "{food_name}" весом {weight} грамм.

СТРОГИЕ ПРАВИЛА:
1. Используй ТОЛЬКО достоверные данные о калорийности на 100г
2. НЕ добавляй калории "на всякий случай"
3. НЕ учитывай способ приготовления если не указан
4. НЕ добавляй масло/соусы если не упомянуты
5. Для напитков без добавок калории = 0-5 ккал
6. Растворимый кофе БЕЗ ДОБАВОК = 2-4 ккал на чашку!

РЕФЕРЕНСНЫЕ ЗНАЧЕНИЯ на 100г:
- Яблоко: 52 ккал, белки 0.3г, жиры 0.2г, углеводы 14г
- Банан: 89 ккал, белки 1.1г, жиры 0.3г, углеводы 23г
- Курица вареная: 165 ккал, белки 31г, жиры 3.6г, углеводы 0г
- Рис вареный: 130 ккал, белки 2.7г, жиры 0.3г, углеводы 28г
- Кофе растворимый БЕЗ добавок: 2 ккал на 100мл!

ФОРМАТ ОТВЕТА (ТОЛЬКО JSON):
{{
    "calories": точное_число_калорий,
    "protein": белки_в_граммах,
    "fat": жиры_в_граммах,
    "carbs": углеводы_в_граммах
}}

Продукт: "{food_name}"
Вес: {weight}г
Рассчитай пропорционально от стандартных значений на 100г.
"""
    
    try:
        # Показываем сообщение об анализе
        analyzing_msg = await message.answer("🤖 <b>Анализирую продукт...</b>")
        
        # Fallback значения для популярных продуктов (кэш) - точные данные на 1г
        fallback_foods = {
            "яблоко": {"calories": 0.52, "protein": 0.003, "fat": 0.002, "carbs": 0.14},
            "банан": {"calories": 0.89, "protein": 0.011, "fat": 0.003, "carbs": 0.23},
            "хлеб": {"calories": 2.64, "protein": 0.089, "fat": 0.033, "carbs": 0.491},
            "курица": {"calories": 1.65, "protein": 0.31, "fat": 0.036, "carbs": 0.0},
            "рис": {"calories": 1.30, "protein": 0.028, "fat": 0.003, "carbs": 0.28},
            "кофе": {"calories": 0.02, "protein": 0.0002, "fat": 0.0, "carbs": 0.0},
            "растворимый кофе": {"calories": 0.02, "protein": 0.0002, "fat": 0.0, "carbs": 0.0},
            "чай": {"calories": 0.01, "protein": 0.0, "fat": 0.0, "carbs": 0.0},
            "вода": {"calories": 0.0, "protein": 0.0, "fat": 0.0, "carbs": 0.0}
        }
        
        # Проверяем есть ли продукт в кэше
        food_lower = food_name.lower()
        for key, values in fallback_foods.items():
            if key in food_lower:
                nutrition_data = {
                    "calories": values["calories"] * weight,
                    "protein": values["protein"] * weight,
                    "fat": values["fat"] * weight,
                    "carbs": values["carbs"] * weight
                }
                await analyzing_msg.edit_text("✅ <b>Продукт найден в базе!</b>")
                break
        else:
            # Получаем анализ от GigaChat только если нет в кэше
            try:
                ai_response = await generate_text_gigachat(prompt=prompt)
                
                # Парсим JSON ответ
                import json
                import re
                
                # Ищем JSON в ответе
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    nutrition_data = json.loads(json_match.group())
                    await analyzing_msg.edit_text("✅ <b>Анализ завершен!</b>")
                else:
                    raise ValueError("Нет JSON в ответе")
            except Exception as e:
                # Fallback значения при ошибке GigaChat
                nutrition_data = {
                    "calories": weight * 1.5,  # Средние значения
                    "protein": weight * 0.05,
                    "fat": weight * 0.02,
                    "carbs": weight * 0.15
                }
                await analyzing_msg.edit_text("⚠️ <b>Использованы приблизительные данные</b>")
        
        calories = nutrition_data.get('calories', 0)
        protein = nutrition_data.get('protein', 0)
        fat = nutrition_data.get('fat', 0)
        carbs = nutrition_data.get('carbs', 0)
        
        # Отправляем запрос на backend для сохранения еды
        payload = {
            'user_id': message.from_user.id,
            'food_name': food_name,
            'weight_grams': weight,
            'date': date,
            'time': time,
            'calories': calories,
            'protein': protein,
            'fat': fat,
            'carbs': carbs
        }
        
        r = requests.post(f'{API_URL}/api/meal', json=payload, timeout=REQUEST_TIMEOUT)
        
        # Удаляем сообщение об анализе
        await analyzing_msg.delete()
        
        if r.status_code == 200:
            await message.answer(
                f"✅ <b>{food_name.title()} ({weight} г) добавлено!</b>\n\n"
                f"📊 <b>Пищевая ценность:</b>\n"
                f"🔥 Калории: {calories:.1f} ккал\n"
                f"🥩 Белки: {protein:.1f} г\n"
                f"🧈 Жиры: {fat:.1f} г\n"
                f"🍞 Углеводы: {carbs:.1f} г",
                reply_markup=kb.main_menu_kb
            )
        else:
            await message.answer("❌ Ошибка сохранения еды", reply_markup=kb.main_menu_kb)
        
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        
    except Exception as e:
        await message.answer(
            f"❌ Произошла ошибка при добавлении еды: {str(e)[:100]}...",
            reply_markup=kb.main_menu_kb
        )
        await state.clear()
        await clear_fsm_state(message.from_user.id)

# --- Preset FSM ---
@router.callback_query(F.data == 'food_templates')
async def food_templates_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Выбрать из шаблонов' при добавлении еды"""
    await callback.answer()
    user_id = callback.from_user.id
    
    try:
        import requests
        r = await safe_api_request('GET', f'{API_URL}/api/presets?user_id={user_id}')
        if r.status_code == 200:
            presets = r.json().get('presets', [])
            if not presets:
                await callback.message.edit_text(
                    "📋 <b>У вас пока нет шаблонов</b>\n\n"
                    "💡 Создайте первый шаблон:\n"
                    "1. Выберите <b>«Мои шаблоны»</b> в главном меню\n"
                    "2. Следуйте инструкциям для создания\n\n"
                    "А пока добавьте еду вручную 👇\n"
                    "📝 Введите: <i>название вес_в_граммах</i>\n"
                    "🍎 Пример: <code>Яблоко 150</code>",
                    reply_markup=kb.back_kb,
                    parse_mode='HTML'
                )
                return
            
            # Формируем клавиатуру с шаблонами
            keyboard = []
            for preset in presets:
                keyboard.append([InlineKeyboardButton(
                    text=f"🍽️ {preset['name']}", 
                    callback_data=f"select_preset_{preset['id']}"
                )])
            
            keyboard.append([InlineKeyboardButton(text='⬅️ Назад к добавлению', callback_data='back_to_add_food')])
            templates_kb = InlineKeyboardMarkup(inline_keyboard=keyboard)
            
            await callback.message.edit_text(
                "🍽️ <b>Выберите шаблон для добавления:</b>\n\n"
                "👆 Нажмите на нужный шаблон выше",
                reply_markup=templates_kb,
                parse_mode='HTML'
            )
        else:
            await callback.message.edit_text(
                "❌ Ошибка получения шаблонов. Попробуйте позже.",
                reply_markup=kb.back_kb
            )
    except Exception as e:
                 await callback.message.edit_text(
             "❌ Ошибка соединения. Попробуйте позже.",
             reply_markup=kb.back_kb
         )

@router.callback_query(F.data.startswith('select_preset_'))
async def select_preset_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора конкретного шаблона"""
    await callback.answer()
    preset_id = int(callback.data.split('_')[-1])
    user_id = callback.from_user.id
    
    try:
        import requests
        r = await safe_api_request('POST', f'{API_URL}/api/add_preset_meals', 
                                 json={'user_id': user_id, 'preset_id': preset_id})
        
        if r.status_code == 200:
            result = r.json()
            await callback.message.edit_text(
                f"✅ <b>Шаблон добавлен!</b>\n\n"
                f"🍽️ <b>{result.get('preset_name', 'Шаблон')}</b>\n"
                f"📊 Калории: {result.get('total_calories', 0):.1f} ккал\n"
                f"🥩 Белки: {result.get('total_protein', 0):.1f} г\n"
                f"🧈 Жиры: {result.get('total_fat', 0):.1f} г\n"
                f"🍞 Углеводы: {result.get('total_carbs', 0):.1f} г\n\n"
                f"📝 Добавлено блюд: {result.get('meals_count', 0)}",
                reply_markup=kb.back_kb,
                parse_mode='HTML'
            )
            
            # Очищаем состояние
            await state.clear()
            await clear_fsm_state(user_id)
        else:
            await callback.message.edit_text(
                "❌ Ошибка добавления шаблона. Попробуйте позже.",
                reply_markup=kb.back_kb
            )
    except Exception as e:
        await callback.message.edit_text(
            "❌ Ошибка соединения. Попробуйте позже.",
            reply_markup=kb.back_kb
        )

@router.callback_query(F.data == 'back_to_add_food')
async def back_to_add_food_callback(callback: CallbackQuery, state: FSMContext):
    """Возврат к форме добавления еды"""
    await callback.answer()
    
    message_text = (
        "🍽️ <b>Добавление еды</b>\n\n"
        "📝 Введите название блюда и вес в граммах\n"
        "💡 <i>Пример: Яблоко 150</i>\n\n"
        "Или выберите готовый шаблон ниже 👇"
    )
    
    await callback.message.edit_text(message_text, reply_markup=kb.add_food_kb, parse_mode='HTML')
    await state.set_state(AddMealFSM.waiting)
    await save_fsm_state(callback.from_user.id, 'AddMealFSM:waiting')

@router.callback_query(F.data == 'presets')
async def presets_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    import requests
    user_id = callback.from_user.id
    try:
        r = requests.get(f'{API_URL}/api/presets?user_id={user_id}', timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            presets = r.json().get('presets', [])
            if not presets:
                await callback.message.answer('<b>У вас нет шаблонов. Напишите название нового шаблона:</b>')
                await state.set_state(PresetFSM.name)
                await save_fsm_state(user_id, 'PresetFSM:name')
                return
            text = '<b>Ваши шаблоны:</b>\n'
            for p in presets:
                text += f"\n{p['id']}: {p['name']} — {len(p['food_items'])} блюд"
            text += '\n\nЧтобы добавить новый, напишите название шаблона.'
            await callback.message.answer(text)
            await state.set_state(PresetFSM.name)
            await save_fsm_state(user_id, 'PresetFSM:name')
        else:
            await callback.message.answer('<b>Ошибка получения шаблонов</b>')
    except Exception as e:
        error_msg = str(e).replace('<', '&lt;').replace('>', '&gt;')
        await callback.message.answer(f'<b>Ошибка соединения с сервером: {error_msg}</b>')

@router.message(PresetFSM.name)
async def preset_name(message: Message, state: FSMContext):
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Создание шаблона отменено", reply_markup=kb.main_menu_kb)
        return
    
    await state.update_data(preset_name=message.text.strip(), food_items=[])
    await save_fsm_state(message.from_user.id, 'PresetFSM:name', {'preset_name': message.text.strip(), 'food_items': []})
    await message.answer('<b>Введите блюдо и вес (пример: Яблоко, 100). Когда закончите, напишите "готово".</b>', reply_markup=kb.back_kb)
    await state.set_state(PresetFSM.food)
    await save_fsm_state(message.from_user.id, 'PresetFSM:food')

@router.message(PresetFSM.food)
async def preset_food(message: Message, state: FSMContext):
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Создание шаблона отменено", reply_markup=kb.main_menu_kb)
        return
    
    if message.text.strip().lower() == 'готово':
        data = await state.get_data()
        import requests
        payload = {
            'user_id': message.from_user.id,
            'name': data['preset_name'],
            'food_items': data['food_items']
        }
        try:
            r = requests.post(f'{API_URL}/api/preset', json=payload, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                await message.answer('<b>Шаблон сохранён!</b>', reply_markup=kb.main_menu_kb)
            else:
                await message.answer('<b>Ошибка сохранения шаблона</b>', reply_markup=kb.main_menu_kb)
        except Exception as e:
            error_msg = str(e).replace('<', '&lt;').replace('>', '&gt;')
            await message.answer(f'<b>Ошибка соединения с сервером: {error_msg}</b>', reply_markup=kb.main_menu_kb)
        finally:
            await state.clear()
            await clear_fsm_state(message.from_user.id)
        return
    
    try:
        food_name, weight = [x.strip() for x in message.text.split(',')]
        weight = float(weight)
    except Exception:
        await message.answer('<b>Формат неверный. Пример: Яблоко, 100</b>', reply_markup=kb.back_kb)
        return
    
    data = await state.get_data()
    food_items = data.get('food_items', [])
    food_items.append({'food_name': food_name, 'weight': weight})
    await state.update_data(food_items=food_items)
    await save_fsm_state(message.from_user.id, 'PresetFSM:food', {'preset_name': data['preset_name'], 'food_items': food_items})
    await message.answer('<b>Добавлено! Введите следующее блюдо или "готово" для завершения.</b>', reply_markup=kb.back_kb)

# --- Трекер воды с FSM ---
@router.message(Command('water'))
@router.message(lambda message: message.text == 'Трекер воды')
async def water_command(message: Message, state: FSMContext):
    # Устанавливаем состояние для трекера воды
    await state.set_state(WaterFSM.add)
    
    # Быстро получаем текущее количество воды из локальной БД
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
        if user:
            from utils.daily_water import ensure_user_water_today
            if ensure_user_water_today(user):
                await session.commit()
        current_water = (user.water_ml or 0) if user else 0
    
    await message.answer(f"Выпито воды: {current_water} мл\n\nВведите количество мл, которое вы выпили:", reply_markup=kb.back_kb)
    await save_fsm_state(message.from_user.id, 'WaterFSM:add')

@router.message(WaterFSM.add)
async def water_add_input(message: Message, state: FSMContext):
    if message.text.lower() == 'назад':
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Действие отменено", reply_markup=kb.main_menu_kb)
        return
        
    try:
        ml = int(message.text.strip())
        if not (0 < ml < 5000):
            raise ValueError
    except:
        await message.answer('<b>Введите количество мл (1-5000)</b>')
        return
    
    # Обновляем воду в локальной базе данных
    async with async_session() as session:
        from utils.daily_water import ensure_user_water_today
        user = await session.get(User, message.from_user.id)
        if not user:
            user = User(tg_id=message.from_user.id, water_ml=ml)
            session.add(user)
        else:
            ensure_user_water_today(user)
            user.water_ml = (user.water_ml or 0) + ml
        await session.commit()
    
    # Также отправляем в API для синхронизации
    import requests
    payload = {'user_id': message.from_user.id, 'ml': ml}
    try:
        r = requests.post(f'{API_URL}/api/water', json=payload, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            await message.answer(f'<b>💧 Записано! Добавлено {ml} мл воды</b>\n\n<b>Всего выпито сегодня: {user.water_ml} мл</b>', reply_markup=kb.main_menu_kb)
        else:
            # Если API недоступен, все равно показываем успех (данные сохранены локально)
            await message.answer(f'<b>💧 Записано! Добавлено {ml} мл воды</b>\n\n<b>Всего выпито сегодня: {user.water_ml} мл</b>', reply_markup=kb.main_menu_kb)
    except:
        # Если API недоступен, все равно показываем успех (данные сохранены локально)
        await message.answer(f'<b>💧 Записано! Добавлено {ml} мл воды</b>\n\n<b>Всего выпито сегодня: {user.water_ml} мл</b>', reply_markup=kb.main_menu_kb)
    
    await state.clear()
    await clear_fsm_state(message.from_user.id)

@router.message(Command('premium'))
async def premium_info(message: Message):
    from components.payment_system.payment_operations import check_premium
    status = check_premium(message.from_user.id)
    await message.answer(f"Премиум {'активен' if status else 'не активен'}.")

@router.callback_query(F.data == 'dietolog')
async def dietolog_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    from components.payment_system.payment_operations import check_premium
    access = check_premium(tg_id=callback.from_user.id)
    if not access:
        await callback.message.answer('<b>Индивидуальный план питания доступен только по премиум-подписке. Оформить: /premium</b>')
        return
    await callback.message.answer('<b>Ваш персональный диетолог скоро будет доступен!</b>')

@router.callback_query(F.data == 'menu')
async def menu_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    import requests
    
    try:
        # Получаем профиль пользователя через API
        r = requests.get(f'{API_URL}/api/profile?tg_id={callback.from_user.id}')
        if r.status_code == 200:
            profile = r.json().get('profile', {})
            if not profile:
                await callback.message.answer("❌ Профиль не найден. Сначала создайте профиль через /profile")
                return
            
            user_data = {
                'name': profile.get('name', 'Пользователь'),
                'age': profile.get('age', 25),
                'gender': profile.get('gender', 'не указан'),
                'weight': profile.get('weight', 70),
                'height': profile.get('height', 170),
                'activity_level': profile.get('activity_level', 2)
            }
        else:
            await callback.message.answer("❌ Ошибка получения профиля. Сначала создайте профиль через /profile")
            return
        
        # Получаем статистику питания за последние 7 дней
        stats_data = {}
        try:
            stats_r = requests.get(f'{API_URL}/api/daily_stats?user_id={callback.from_user.id}&days=7')
            if stats_r.status_code == 200:
                stats_data = stats_r.json().get('daily_stats', [])
        except:
            pass
        
        # Рассчитываем базовый метаболизм (BMR) по формуле Миффлина-Сан Жеора
        if user_data['gender'].lower() in ['м', 'мужской', 'male']:
            bmr = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age'] + 5
        else:
            bmr = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age'] - 161
        
        # Коэффициенты активности
        activity_coefficients = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
        tdee = bmr * activity_coefficients.get(user_data['activity_level'], 1.375)
        
        # Анализируем статистику питания
        avg_calories = 0
        avg_protein = 0
        avg_fat = 0
        avg_carbs = 0
        
        if stats_data:
            total_days = len(stats_data)
            total_calories = sum(day.get('calories', 0) for day in stats_data)
            total_protein = sum(day.get('protein', 0) for day in stats_data)
            total_fat = sum(day.get('fat', 0) for day in stats_data)
            total_carbs = sum(day.get('carbs', 0) for day in stats_data)
            
            if total_days > 0:
                avg_calories = total_calories / total_days
                avg_protein = total_protein / total_days
                avg_fat = total_fat / total_days
                avg_carbs = total_carbs / total_days
        
        # Формируем рекомендации на основе статистики
        recommendations = ""
        if avg_calories > 0:
            if avg_calories > tdee * 1.1:
                recommendations += "📊 За последние дни вы потребляли больше калорий, чем нужно. Рекомендую снизить порции.\n"
            elif avg_calories < tdee * 0.9:
                recommendations += "📊 За последние дни вы потребляли меньше калорий, чем нужно. Рекомендую увеличить порции.\n"
            
            if avg_protein < user_data['weight'] * 1.2:
                recommendations += "🥩 Недостаточно белка в рационе. Добавьте больше белковых продуктов.\n"
            if avg_fat > tdee * 0.35 / 9:
                recommendations += "🧈 Слишком много жиров. Уменьшите потребление жирных продуктов.\n"
        
        # Генерируем меню с помощью GigaChat
        prompt = f"""
Ты профессиональный диетолог. Создай персональное меню на день для клиента:

ДАННЫЕ КЛИЕНТА:
- Имя: {user_data['name']}
- Возраст: {user_data['age']} лет
- Пол: {user_data['gender']}
- Вес: {user_data['weight']} кг
- Рост: {user_data['height']} см
- Уровень активности: {user_data['activity_level']}/5
- Потребность в калориях: {tdee:.0f} ккал/день

АНАЛИЗ ПИТАНИЯ ЗА ПОСЛЕДНИЕ 7 ДНЕЙ:
- Среднее потребление калорий: {avg_calories:.0f} ккал/день
- Среднее потребление белков: {avg_protein:.1f} г/день
- Среднее потребление жиров: {avg_fat:.1f} г/день
- Среднее потребление углеводов: {avg_carbs:.1f} г/день

РЕКОМЕНДАЦИИ:
{recommendations}

СОЗДАЙ СБАЛАНСИРОВАННОЕ МЕНЮ НА ДЕНЬ:

1. 🍳 ЗАВТРАК ({tdee*0.25:.0f} ккал)
2. 🍽️ ОБЕД ({tdee*0.35:.0f} ккал)
3. 🍴 УЖИН ({tdee*0.25:.0f} ккал)
4. 🍎 ПЕРЕКУСЫ ({tdee*0.15:.0f} ккал)

Для каждого приема пищи укажи:
- Названия блюд и продуктов
- Точные порции в граммах
- Калорийность каждого блюда
- Белки, жиры, углеводы

Меню должно быть:
- Разнообразным и вкусным
- Соответствовать потребностям в калориях
- Включать все необходимые нутриенты
- Практичным для приготовления
- Учитывать рекомендации по корректировке рациона

Формат ответа: структурированный текст с эмодзи для лучшего восприятия.
"""
        
        waiting_msg = await callback.message.answer("🍽️ <b>Генерирую персональное меню с учетом вашей статистики...</b>")
        menu_response = await generate_text_gigachat(prompt=prompt)
        
        await waiting_msg.delete()
        
        # Добавляем краткую статистику к ответу
        stats_summary = ""
        if avg_calories > 0:
            stats_summary = f"\n\n📊 <b>Ваша статистика за 7 дней:</b>\n"
            stats_summary += f"🔥 Средние калории: {avg_calories:.0f} ккал/день\n"
            stats_summary += f"🥩 Средние белки: {avg_protein:.1f} г/день\n"
            stats_summary += f"🧈 Средние жиры: {avg_fat:.1f} г/день\n"
            stats_summary += f"🍞 Средние углеводы: {avg_carbs:.1f} г/день\n"
            stats_summary += f"📈 Целевые калории: {tdee:.0f} ккал/день"
        
        await callback.message.answer(
            f"🍽️ <b>Персональное меню для {user_data['name']}</b>\n\n{menu_response}{stats_summary}", 
            reply_markup=kb.main_menu_kb
        )
        
    except Exception as e:
        await callback.message.answer("❌ Ошибка генерации меню. Попробуйте позже.", reply_markup=kb.main_menu_kb)

# Распознавание еды на фото и генерация изображений доступны всем — премиум не требуется.

@router.callback_query(F.data == 'recognize_image')
async def recognize_image_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer('<b>Скоро здесь появится распознавание еды на фото!</b>')

def fake_callback_query(message):
    return type(
        'FakeCallbackQuery', (), {
            'from_user': message.from_user,
            'message': message,
            'answer': lambda *args, **kwargs: None
        }
    )()

# --- Для всех команд реализую реальные действия ---
# /profile
@router.message(Command('profile'))
@router.message(lambda message: message.text == 'Профиль')
async def profile_command(message: Message, state: FSMContext):
    # Очищаем состояние только для профиля
    await state.clear()
    
    # Проверяем профиль пользователя
    import requests
    user_id = message.from_user.id
    try:
        r = requests.get(f'{API_URL}/api/profile?tg_id={user_id}')
        if r.status_code == 200:
            profile = r.json().get('profile')
            if not profile or not profile.get('name'):
                await message.answer('<b>Профиль не заполнен. Давайте заполним!</b>\nВведите ваше имя:')
                await state.set_state(ProfileFSM.name)
            else:
                profile_text = f"<b>👤 Ваш профиль:</b>\n\n"
                profile_text += f"👤 Имя: {profile.get('name', 'Не указано')}\n"
                profile_text += f"🎂 Возраст: {profile.get('age', 'Не указан')}\n"
                profile_text += f"⚥ Пол: {profile.get('gender', 'Не указан')}\n"
                profile_text += f"⚖️ Вес: {profile.get('weight', 'Не указан')} кг\n"
                profile_text += f"📏 Рост: {profile.get('height', 'Не указан')} см\n"
                profile_text += f"🏃 Активность: {profile.get('activity_level', 'Не указана')}\n"
                
                if profile.get('bmr'):
                    profile_text += f"\n🔥 Базовый метаболизм: {profile['bmr']} ккал/день"
                if profile.get('daily_calories'):
                    profile_text += f"\n🍽️ Дневная норма: {profile['daily_calories']} ккал"
                
                await message.answer(profile_text, reply_markup=kb.profile_kb)
        else:
            await message.answer('<b>Профиль не найден. Давайте создадим!</b>\nВведите ваше имя:')
            await state.set_state(ProfileFSM.name)
    except Exception as e:
        await message.answer('<b>Ошибка получения профиля. Давайте создадим новый!</b>\nВведите ваше имя:')
        await state.set_state(ProfileFSM.name)

# /history
@router.message(Command('history'))
@router.message(lambda message: message.text == 'История приёмов пищи')
async def history_command(message: Message, state: FSMContext):
    # Очищаем состояние только для истории
    await state.clear()
    
    import requests
    try:
        r = requests.get(f'{API_URL}/api/meals?user_id={message.from_user.id}')
        if r.status_code == 200:
            meals = r.json().get('meals', [])
            if not meals:
                await message.answer("<b>История пуста.</b>")
            else:
                text = "<b>🍽️ История приёмов пищи:</b>\n\n"
                for m in meals[-10:]:
                    text += f"📅 {m['date']} {m['time']}: {m['food_name']} — {m['weight_grams']} г, {m['calories']} ккал\n"
                await message.answer(text)
        else:
            await message.answer('<b>Ошибка получения истории</b>')
    except Exception as e:
        error_msg = str(e).replace('<', '&lt;').replace('>', '&gt;')
        await message.answer(f'<b>Ошибка соединения с сервером: {error_msg}</b>')

# /presets
@router.message(Command('presets'))
@router.message(lambda message: message.text == 'Мои шаблоны')
async def presets_command(message: Message, state: FSMContext):
    # Очищаем состояние только для шаблонов
    await state.clear()
    await clear_fsm_state(message.from_user.id)
    
    async with async_session() as session:
        presets = await session.execute(select(Preset).where(Preset.user_id == message.from_user.id))
        presets = presets.scalars().all()
        
        if not presets:
            await message.answer(
                "<b>📋 У вас пока нет шаблонов</b>\n\n"
                "🎯 <b>Что такое шаблоны?</b>\n"
                "Шаблоны — это готовые наборы блюд, которые вы часто едите вместе.\n\n"
                "💡 <b>Примеры шаблонов:</b>\n"
                "• Завтрак: овсянка + банан + кофе\n"
                "• Обед: курица + рис + овощи\n"
                "• Перекус: яблоко + орехи\n\n"
                "📝 <b>Как создать шаблон:</b>\n"
                "1. Нажмите 'Добавить шаблон' ниже\n"
                "2. Введите название шаблона\n"
                "3. Добавьте продукты и их вес\n"
                "4. Напишите 'готово' для сохранения\n\n"
                "🚀 <b>Преимущества шаблонов:</b>\n"
                "• Быстрое добавление привычных приемов пищи\n"
                "• Экономия времени\n"
                "• Точный подсчет калорий\n\n"
                "💡 <i>Попробуйте создать свой первый шаблон прямо сейчас!</i>",
                reply_markup=kb.create_template_kb
            )
        else:
            # Используем Mistral AI для анализа шаблонов
            prompt = f"""
Ты эксперт по питанию. Проанализируй шаблоны пользователя и дай рекомендации:

Шаблоны пользователя:
{chr(10).join([f"- {p.name}: {p.food_items}" for p in presets])}

Дай анализ в формате:
1. 📊 Общая оценка шаблонов
2. ✅ Сильные стороны
3. ⚠️ Что можно улучшить
4. 💡 Рекомендации по питанию
5. 🎯 Идеи для новых шаблонов

Будь дружелюбным и поддерживающим. Используй эмодзи для лучшего восприятия.
"""
            
            try:
                analysis = await generate_text_gigachat(prompt=prompt)
                
                text = "<b>📋 Ваши шаблоны:</b>\n\n"
                for i, p in enumerate(presets, 1):
                    text += f"{i}. <b>{p.name}</b>\n   {p.food_items}\n\n"
                
                text += f"\n🤖 <b>Анализ от ИИ-диетолога:</b>\n\n{analysis}"
                
                # Разбиваем на части если текст слишком длинный
                if len(text) > 4000:
                    parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
                    for i, part in enumerate(parts):
                        if i == 0:
                            await message.answer(part)
                        else:
                            await message.answer(f"<b>📋 Шаблоны (продолжение {i+1}):</b>\n\n{part}")
                else:
                    await message.answer(text)
                    
            except Exception as e:
                # Fallback без ИИ анализа
                text = "<b>📋 Ваши шаблоны:</b>\n\n"
                for i, p in enumerate(presets, 1):
                    text += f"{i}. <b>{p.name}</b>\n   {p.food_items}\n\n"
                text += "💡 <b>Совет:</b> Используйте шаблоны для быстрого добавления привычных приемов пищи!"
                await message.answer(text)

@router.callback_query(F.data == 'create_template')
async def create_template_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки создания нового шаблона"""
    await callback.answer()
    await callback.message.edit_text(
        "<b>📝 Создание нового шаблона</b>\n\n"
        "💡 <b>Простой формат:</b>\n"
        "Введите всё в одну строку:\n\n"
        "• <b>С названием:</b>\n"
        "Завтрак: яичница из двух яиц 200 + кофе без сахара 250\n\n"
        "• <b>Без названия:</b>\n"
        "яичница из двух яиц 200 + кофе без сахара 250\n\n"
        "✏️ <b>Введите шаблон:</b>",
        reply_markup=kb.back_kb
    )
    await state.set_state(SimplePresetFSM.waiting)
    await save_fsm_state(callback.from_user.id, 'SimplePresetFSM:waiting')

@router.callback_query(F.data == 'create_template_from_addmeal')
async def create_template_from_addmeal_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки создания шаблона из меню добавления еды"""
    await callback.answer()
    await callback.message.edit_text(
        "<b>📝 Создание нового шаблона</b>\n\n"
        "💡 <b>Простой формат:</b>\n"
        "Введите всё в одну строку:\n\n"
        "• <b>С названием:</b>\n"
        "Завтрак: яичница из двух яиц 200 + кофе без сахара 250\n\n"
        "• <b>Без названия:</b>\n"
        "яичница из двух яиц 200 + кофе без сахара 250\n\n"
        "✏️ <b>Введите шаблон:</b>",
        reply_markup=kb.back_kb
    )
    await state.set_state(SimplePresetFSM.waiting)
    await save_fsm_state(callback.from_user.id, 'SimplePresetFSM:waiting')

@router.message(SimplePresetFSM.waiting)
async def simple_preset_waiting(message: Message, state: FSMContext):
    """Обработчик простого создания шаблона"""
    if message.text.lower() == 'назад':
        await state.clear()
        await clear_fsm_state(message.from_user.id)
        await message.answer("Действие отменено", reply_markup=kb.main_menu_kb)
        return
    
    try:
        # Парсим простой формат
        name, food_items = parse_simple_preset(message.text)
        
        # Сохраняем шаблон
        import requests
        payload = {
            'user_id': message.from_user.id,
            'name': name,
            'food_items': food_items
        }
        
        r = requests.post(f'{API_URL}/api/preset', json=payload, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            # Формируем ответ с информацией о созданном шаблоне
            response = f"✅ <b>Шаблон '{name}' создан!</b>\n\n"
            response += "<b>Содержимое:</b>\n"
            total_calories = 0
            
            for item in food_items:
                response += f"• {item['food_name']} - {item['weight']}г\n"
                # Примерный расчет калорий (можно улучшить)
                estimated_calories = int(item['weight'] * 0.8)  # Примерно 80 ккал на 100г
                total_calories += estimated_calories
            
            response += f"\n📊 <b>Примерная калорийность:</b> {total_calories} ккал"
            
            await message.answer(response, reply_markup=kb.main_menu_kb)
        else:
            await message.answer('<b>❌ Ошибка сохранения шаблона</b>', reply_markup=kb.main_menu_kb)
            
    except ValueError as e:
        await message.answer(
            f"❌ <b>Ошибка в формате:</b>\n{str(e)}\n\n"
            "💡 <b>Правильный формат:</b>\n"
            "• Завтрак: яичница из двух яиц 200 + кофе без сахара 250\n"
            "• яичница из двух яиц 200 + кофе без сахара 250",
            reply_markup=kb.back_kb
        )
        return
    except Exception as e:
        error_msg = str(e).replace('<', '&lt;').replace('>', '&gt;')
        await message.answer(f'<b>❌ Ошибка соединения с сервером: {error_msg}</b>', reply_markup=kb.main_menu_kb)
    finally:
        await state.clear()
        await clear_fsm_state(message.from_user.id)

# /dietolog
@router.message(Command('dietolog'))
@router.message(lambda message: message.text == 'Личный диетолог')
async def dietolog_command(message: Message, state: FSMContext):
    # Очищаем состояние только для диетолога
    await state.clear()
    
    # Проверяем подписку на диетолога
    from components.payment_system.payment_operations import PaymentManager
    has_subscription = await PaymentManager.check_subscription(message.from_user.id, 'diet_consultant')
    
    if has_subscription:
        await message.answer(
            '<b>👨‍⚕️ Добро пожаловать на консультацию к диетологу!\n\n'
            'Я готов помочь вам с:\n'
            '• Анализом вашего рациона\n'
            '• Рекомендациями по питанию\n'
            '• Составлением планов питания\n'
            '• Расчетом калорий и БЖУ\n'
            '• Советами по снижению/набору веса\n'
            '• Мотивацией и поддержкой\n\n'
            'Просто напишите ваш вопрос или опишите ситуацию, и я дам профессиональную консультацию!\n\n'
            'Для завершения консультации используйте /stop</b>'
        )
        await state.set_state(Chat.active)
    else:
        # Показываем информацию о подписке
        await message.answer(
            "👨‍⚕️ <b>Личный диетолог</b>\n\n"
            "Получите персональные консультации от ИИ-диетолога:\n"
            "• Ответы на любые вопросы о питании\n"
            "• Персональные рекомендации по диете\n"
            "• Анализ вашего рациона\n"
            "• Советы по достижению целей\n\n"
            "💰 <b>Стоимость:</b> 50₽ за месяц\n\n"
            "Для покупки подписки используйте команду: /diet_consultant",
            parse_mode="HTML"
        )

# /menu
@router.message(Command('menu'))
@router.message(lambda message: message.text == 'Сгенерировать меню')
async def menu_command(message: Message, state: FSMContext):
    # Очищаем состояние только для меню
    await state.clear()
    
    # Проверяем подписку на генерацию меню
    from components.payment_system.payment_operations import PaymentManager
    has_subscription = await PaymentManager.check_subscription(message.from_user.id, 'menu_generator')
    
    if not has_subscription:
        # Показываем информацию о подписке
        await message.answer(
            "🍽️ <b>Генерация персонального меню</b>\n\n"
            "Получите персональное меню, созданное специально для вас:\n"
            "• Учет ваших целей и предпочтений\n"
            "• Сбалансированное питание\n"
            "• Разнообразные блюда\n"
            "• Подробные рецепты\n\n"
            "💰 <b>Стоимость:</b> 100₽ за месяц\n\n"
            "Для покупки подписки используйте команду: /menu_generator",
            parse_mode="HTML"
        )
        return
    
    try:
        # Получаем профиль пользователя через API
        r = requests.get(f'{API_URL}/api/profile?tg_id={message.from_user.id}')
        if r.status_code == 200:
            profile = r.json().get('profile', {})
            if not profile:
                await message.answer("❌ Профиль не найден. Сначала создайте профиль через /profile")
                return
            
            user_data = {
                'name': profile.get('name', 'Пользователь'),
                'age': profile.get('age', 25),
                'gender': profile.get('gender', 'не указан'),
                'weight': profile.get('weight', 70),
                'height': profile.get('height', 170),
                'activity_level': profile.get('activity_level', 2)
            }
        else:
            await message.answer("❌ Ошибка получения профиля. Сначала создайте профиль через /profile")
            return
        
        # Рассчитываем базовый метаболизм (BMR) по формуле Миффлина-Сан Жеора
        if user_data['gender'].lower() == 'мужской':
            bmr = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age'] + 5
        else:
            bmr = 10 * user_data['weight'] + 6.25 * user_data['height'] - 5 * user_data['age'] - 161
        
        # Коэффициенты активности
        activity_coefficients = {1: 1.2, 2: 1.375, 3: 1.55, 4: 1.725, 5: 1.9}
        tdee = bmr * activity_coefficients.get(user_data['activity_level'], 1.375)
        
        # Генерируем меню с помощью GigaChat
        prompt = f"""
Ты профессиональный диетолог. Создай персональное меню на день для клиента:

Данные клиента:
- Имя: {user_data['name']}
- Возраст: {user_data['age']} лет
- Пол: {user_data['gender']}
- Вес: {user_data['weight']} кг
- Рост: {user_data['height']} см
- Уровень активности: {user_data['activity_level']}
- Потребность в калориях: {tdee:.0f} ккал/день

Создай сбалансированное меню на день с указанием:

1. 🍳 ЗАВТРАК (25% от дневной нормы - {tdee*0.25:.0f} ккал)
2. 🍽️ ОБЕД (35% от дневной нормы - {tdee*0.35:.0f} ккал)
3. 🍴 УЖИН (25% от дневной нормы - {tdee*0.25:.0f} ккал)
4. 🍎 ПЕРЕКУСЫ (15% от дневной нормы - {tdee*0.15:.0f} ккал)

Для каждого приема пищи укажи:
- Названия блюд и продуктов
- Точные порции в граммах
- Калорийность каждого блюда
- Белки, жиры, углеводы

Меню должно быть:
- Разнообразным и вкусным
- Соответствовать потребностям в калориях
- Включать все необходимые нутриенты
- Практичным для приготовления

Формат ответа: структурированный текст с эмодзи для лучшего восприятия.
"""
        
        waiting_msg = await message.answer("🍽️ <b>Генерирую персональное меню...</b>")
        menu_response = await generate_text_gigachat(prompt=prompt)
        
        await waiting_msg.delete()
        await message.answer(
            f"🍽️ <b>Персональное меню для {user_data['name']}</b>\n\n{menu_response}", 
            reply_markup=kb.main_menu_kb
        )
        
    except Exception as e:
        await message.answer("❌ Ошибка генерации меню. Попробуйте позже.", reply_markup=kb.main_menu_kb)

# /recognize
@router.message(Command('recognize'))
@router.message(lambda message: message.text == 'Распознать еду на фото')
async def recognize_food_command(message: Message, state: FSMContext):
    """Заглушка для распознавания еды по фото"""
    # Очищаем состояние только для распознавания
    await state.clear()
    await clear_fsm_state(message.from_user.id)
    
    await message.answer(
        "<b>📸 Распознавание еды по фото</b>\n\n"
        "🔮 <i>Эта функция появится в грядущих обновлениях!</i>\n\n"
        "В будущем вы сможете:\n"
        "• Сфотографировать блюдо\n"
        "• Автоматически определить калорийность\n"
        "• Получить информацию о БЖУ\n"
        "• Добавить в дневник одним нажатием\n\n"
        "Пока что используйте кнопку <b>«Добавить еду»</b> для ручного ввода 😊"
    )

@router.message(Command('score'))
@router.message(lambda message: message.text == 'Баллы и прогресс')
async def score_command(message: Message, state: FSMContext):
    # Очищаем состояние только для баллов
    await state.clear()
    await clear_fsm_state(message.from_user.id)
    
    # Быстро показываем базовую информацию из локальной БД
    async with async_session() as session:
        user = await session.get(User, message.from_user.id)
        if not user:
            await message.answer("Пользователь не найден в базе данных.")
            return
        
        # Импортируем правильную функцию check_premium
        from components.payment_system.payment_operations import check_premium
        
        # Быстро показываем то, что у нас есть в локальной БД
        progress_text = f"<b>📊 Ваш прогресс:</b>\n\n"
        progress_text += f"⭐ Очки активности: {user.score or 0} (за каждый прием пищи +1)\n"
        progress_text += f"🔥 Дней подряд ведете дневник: {user.streak_days or 0}\n"
        progress_text += f"💧 Вода сегодня: {user.water_ml or 0} мл\n"
        progress_text += f"💎 Премиум: {'активен' if check_premium(user.tg_id) else 'нет'}\n\n"
        progress_text += f"<i>⏳ Загружаем статистику питания...</i>"
        
        # Отправляем быстрый ответ
        sent_message = await message.answer(progress_text)
        
        # Теперь асинхронно пытаемся получить статистику питания с коротким таймаутом
        import requests
        try:
            # Короткий таймаут для быстрого ответа
            r = requests.get(f'{API_URL}/api/stats?user_id={message.from_user.id}', timeout=5)
            if r.status_code == 200:
                stats = r.json().get('stats', {})
                
                # Обновляем сообщение с полной статистикой
                updated_text = f"<b>📊 Ваш прогресс за сегодня:</b>\n\n"
                updated_text += f"🔥 Калории: {stats.get('total_calories', 0):.0f} ккал\n"
                updated_text += f"🍽️ Приемов пищи: {stats.get('total_meals', 0)}\n"
                updated_text += f"💧 Вода: {user.water_ml or 0} мл\n\n"
                updated_text += f"<b>🏆 Общая статистика:</b>\n"
                updated_text += f"⭐ Очки активности: {user.score or 0} (за каждый прием пищи +1)\n"
                updated_text += f"🔥 Дней подряд ведете дневник: {user.streak_days or 0}\n"
                updated_text += f"💎 Премиум: {'активен' if check_premium(user.tg_id) else 'нет'}\n\n"
                updated_text += f"<i>💡 Премиум активируется автоматически при стрике 7+ дней!</i>"
                
                await sent_message.edit_text(updated_text)
            else:
                # Если API не отвечает, просто убираем "загружаем"
                final_text = f"<b>📊 Ваш прогресс:</b>\n\n"
                final_text += f"⭐ Очки активности: {user.score or 0} (за каждый прием пищи +1)\n"
                final_text += f"🔥 Дней подряд ведете дневник: {user.streak_days or 0}\n"
                final_text += f"💧 Вода сегодня: {user.water_ml or 0} мл\n"
                final_text += f"💎 Премиум: {'активен' if check_premium(user.tg_id) else 'нет'}\n\n"
                final_text += f"<i>💡 Ведите дневник каждый день для получения стрика!</i>"
                await sent_message.edit_text(final_text)
        except Exception as e:
            # В случае ошибки просто убираем "загружаем"
            final_text = f"<b>📊 Ваш прогресс:</b>\n\n"
            final_text += f"⭐ Очки активности: {user.score or 0} (за каждый прием пищи +1)\n"
            final_text += f"🔥 Дней подряд ведете дневник: {user.streak_days or 0}\n"
            final_text += f"💧 Вода сегодня: {user.water_ml or 0} мл\n"
            final_text += f"💎 Премиум: {'активен' if check_premium(user.tg_id) else 'нет'}\n\n"
            final_text += f"<i>💡 Ведите дневник каждый день для получения стрика!</i>"
            await sent_message.edit_text(final_text)

@router.message(Command('statistics'))
@router.message(lambda message: message.text == 'Статистика')
async def statistics_command(message: Message, state: FSMContext):
    """Показывает детальную статистику по дням"""
    # Очищаем состояние только для статистики
    await state.clear()
    await clear_fsm_state(message.from_user.id)
    
    # Быстро отправляем сообщение о загрузке
    loading_msg = await message.answer("<b>📊 Загружаем вашу статистику...</b>")
    
    import requests
    try:
        # Короткий таймаут для быстрого ответа
        r = requests.get(f'{API_URL}/api/daily_stats?user_id={message.from_user.id}&days=7', timeout=8)
        if r.status_code == 200:
            data = r.json().get('daily_stats', [])
            
            if not data:
                await loading_msg.edit_text("<b>📊 Статистика пуста. Начните отслеживать питание!</b>")
                return
            
            stats_text = "<b>📊 Ваша статистика за последние 7 дней:</b>\n\n"
            
            for day_stat in data[:5]:  # Показываем только 5 последних дней для скорости
                date = day_stat['date']
                calories = day_stat.get('total_calories', 0) or day_stat.get('calories', 0)
                meals = day_stat.get('total_meals', 0) or day_stat.get('meal_count', 0)
                
                stats_text += f"📅 <b>{date}</b>\n"
                stats_text += f"🔥 Калории: {calories:.0f} ккал\n"
                stats_text += f"🍽️ Приемов пищи: {meals}\n\n"
            
            if len(data) > 5:
                stats_text += f"<i>... и еще {len(data) - 5} дней в истории</i>\n\n"
            
            stats_text += f"<i>💡 Используйте /history для просмотра всех приемов пищи</i>"
            
            await loading_msg.edit_text(stats_text)
        else:
            await loading_msg.edit_text("<b>❌ Не удалось загрузить статистику. Попробуйте позже.</b>")
            
    except Exception as e:
        # Быстрый fallback при ошибке
        error_text = "<b>❌ Сервер временно недоступен</b>\n\n"
        error_text += f"<i>Ошибка: {str(e)[:50]}...</i>\n\n"
        error_text += f"💡 Попробуйте:\n"
        error_text += f"• Проверить интернет соединение\n"
        error_text += f"• Повторить попытку через минуту\n"
        error_text += f"• Использовать /addmeal для добавления еды"
        await loading_msg.edit_text(error_text)

# Обработчик "Мои подписки" - должен быть перед fallback
@router.message(lambda message: message.text == '💳 Мои подписки')
async def my_subscriptions_handler(message: Message):
    """Показывает информацию о подписках пользователя"""
    import sys, traceback
    print("DEBUG: my_subscriptions_handler called", file=sys.stderr)
    print(f"DEBUG: Message text: '{message.text}'", file=sys.stderr)
    print(f"DEBUG: Message text == '💳 Мои подписки': {message.text == '💳 Мои подписки'}", file=sys.stderr)
    user_id = message.from_user.id
    
    try:
        # Проверяем подписки напрямую из базы данных
        from database.init_database import async_session, Subscription
        from sqlalchemy import select, and_
        from datetime import datetime
        
        print(f"DEBUG: Checking subscriptions for user {user_id}", file=sys.stderr)
        
        async with async_session() as session:
            # Получаем активные подписки
            diet_subscription = await session.execute(
                select(Subscription).where(
                    and_(
                        Subscription.user_id == user_id,
                        Subscription.subscription_type == 'diet_consultant',
                        Subscription.status == 'completed',
                        Subscription.end_date > datetime.utcnow()
                    )
                ).order_by(Subscription.end_date.desc())
            )
            diet_subscription = diet_subscription.scalar_one_or_none()
            
            menu_subscription = await session.execute(
                select(Subscription).where(
                    and_(
                        Subscription.user_id == user_id,
                        Subscription.subscription_type == 'menu_generator',
                        Subscription.status == 'completed',
                        Subscription.end_date > datetime.utcnow()
                    )
                ).order_by(Subscription.end_date.desc())
            )
            menu_subscription = menu_subscription.scalar_one_or_none()
        
        print(f"DEBUG: diet_subscription found: {diet_subscription is not None}", file=sys.stderr)
        print(f"DEBUG: menu_subscription found: {menu_subscription is not None}", file=sys.stderr)
        
        response = "📋 <b>Ваши подписки:</b>\n\n"
        
        # Информация о подписке на диетолога
        if diet_subscription:
            days_left = (diet_subscription.end_date - datetime.utcnow()).days
            response += f"👨‍⚕️ <b>Личный диетолог:</b> ✅ Активна\n"
            response += f"⏰ Осталось дней: {days_left}\n"
            response += f"📅 Действует до: {diet_subscription.end_date.strftime('%d.%m.%Y')}\n\n"
        else:
            response += "👨‍⚕️ <b>Личный диетолог:</b> ❌ Неактивна\n\n"
        
        # Информация о подписке на меню
        if menu_subscription:
            days_left = (menu_subscription.end_date - datetime.utcnow()).days
            response += f"🍽️ <b>Генерация меню:</b> ✅ Активна\n"
            response += f"⏰ Осталось дней: {days_left}\n"
            response += f"📅 Действует до: {menu_subscription.end_date.strftime('%d.%m.%Y')}\n\n"
        else:
            response += "🍽️ <b>Генерация меню:</b> ❌ Неактивна\n\n"
        
        # Добавляем информацию о том, как получить подписки
        if not diet_subscription and not menu_subscription:
            response += "💡 <b>Как получить подписки:</b>\n"
            response += "• Нажмите 'Личный диетолог' для консультаций\n"
            response += "• Нажмите 'Сгенерировать меню' для персонального меню\n"
            response += "• При первом использовании вам предложат оплату\n"
        
        print(f"DEBUG: Sending response: {response[:100]}...", file=sys.stderr)
        await message.answer(response, parse_mode="HTML")
        
    except Exception as e:
        print("DEBUG: my_subscriptions_handler exception", file=sys.stderr)
        traceback.print_exc()
        await message.answer("❌ Ошибка получения информации о подписках")
        print(f"Ошибка получения подписок: {e}")

# Catch-all хендлер в самом конце
@router.message()
async def other(message: Message, state: FSMContext):
    """Обработчик всех остальных сообщений"""
    # Проверяем, не находимся ли мы в каком-то состоянии
    current_state = await state.get_state()
    
    if current_state:
        # Если в состоянии, предлагаем сбросить
        await message.answer(
            "🤔 Похоже, вы находитесь в режиме ввода данных. "
            "Используйте /reset_state чтобы сбросить состояние или /help для помощи.",
            reply_markup=kb.main_menu_kb
        )
    else:
        # Если не в состоянии, показываем главное меню
        await message.answer(
            "👋 Привет! Я ваш персональный диетолог. Выберите действие:",
            reply_markup=kb.main_menu_kb
        )

@router.message(Command('reset_state'))
async def reset_state_command(message: Message, state: FSMContext):
    """Команда для сброса состояния FSM"""
    await state.clear()
    await clear_fsm_state(message.from_user.id)
    await message.answer("✅ Состояние сброшено! Теперь можете использовать бота нормально.", reply_markup=kb.main_menu_kb)

@router.message(Command('help'))
async def help_command(message: Message):
    """Команда помощи"""
    help_text = """
🤖 <b>Команды бота:</b>

🍽️ <b>Основные функции:</b>
• /addmeal - Добавить еду
• /profile - Профиль
• /history - История приёмов пищи
• /presets - Мои шаблоны
• /water - Трекер воды
• /mood - Трекер настроения

💡 <b>Если бот заблокирован:</b>
• /reset_state - Сбросить состояние
• /stop - Остановить диалог

🎯 <b>Премиум функции:</b>
• /dietolog - Личный диетолог
• /menu - Сгенерировать меню

📊 <b>Статистика:</b>
• /score - Баллы и прогресс
• /statistics - Статистика

🆘 <b>Помощь:</b>
• /help - Это сообщение
• /info - Информация о боте
"""
    await message.answer(help_text, parse_mode='HTML', reply_markup=kb.main_menu_kb)

# Функция для безопасных API запросов с retry
async def safe_api_request(method, url, **kwargs):
    """Безопасный API запрос с повторными попытками"""
    import time
    max_retries = 3
    base_delay = 1
    
    for attempt in range(max_retries):
        try:
            if method == 'GET':
                response = requests.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
            else:
                response = requests.post(url, timeout=REQUEST_TIMEOUT, **kwargs)
            
            if response.status_code == 200:
                return response
            elif response.status_code >= 500:  # Серверная ошибка - повторяем
                if attempt < max_retries - 1:
                    await asyncio.sleep(base_delay * (2 ** attempt))
                    continue
            return response
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(base_delay * (2 ** attempt))
                continue
            # Возвращаем mock ответ при полном отказе
            class MockResponse:
                status_code = 500
                def json(self): return {}
            return MockResponse()
    
    class MockResponse:
        status_code = 500
        def json(self): return {}
    return MockResponse()

# Функция для парсинга простого формата шаблона
def parse_simple_preset(text: str) -> tuple[str, list]:
    """
    Парсит простой формат шаблона: "название: блюдо1 вес1 + блюдо2 вес2"
    Пример: "Завтрак: яичница из двух яиц 200 + кофе без сахара 250"
    """
    try:
        # Разделяем на название и блюда
        if ':' in text:
            name_part, foods_part = text.split(':', 1)
            name = name_part.strip()
            foods_text = foods_part.strip()
        else:
            # Если нет двоеточия, считаем что название - первое слово
            parts = text.split('+', 1)
            if len(parts) == 1:
                raise ValueError("Не найдены блюда")
            name = parts[0].split()[0]  # Первое слово как название
            foods_text = text
        
        # Разделяем блюда по "+"
        food_items = []
        foods_list = foods_text.split('+')
        
        for food_item in foods_list:
            food_item = food_item.strip()
            if not food_item:
                continue
                
            # Ищем вес в конце (последнее число)
            words = food_item.split()
            if len(words) < 2:
                continue
                
            # Проверяем, является ли последнее слово числом
            try:
                weight = float(words[-1])
                food_name = ' '.join(words[:-1])
            except ValueError:
                # Если последнее слово не число, используем весь текст как название
                food_name = food_item
                weight = 100  # Вес по умолчанию
            
            food_items.append({
                'food_name': food_name.strip(),
                'weight': weight
            })
        
        if not food_items:
            raise ValueError("Не найдены блюда")
            
        return name, food_items
        
    except Exception as e:
        raise ValueError(f"Ошибка парсинга: {str(e)}")
