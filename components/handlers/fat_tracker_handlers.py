import os
import asyncio
from datetime import datetime, date
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy import select, desc, and_

from database.init_database import async_session, User, FatTracking
from components.states.user_states import FatTracker
from components.keyboards.user_kb import fat_tracker_kb, fat_confirm_kb, back_kb
from api.ai_api.fat_calculator import FatPercentageCalculator
from api.ai_api.generate_text import answer_to_text_prompt

router = Router()

@router.message(F.text == 'Трекер жировой массы')
async def fat_tracker_menu(message: Message):
    """Главное меню трекера жировой массы"""
    try:
        # Получаем последнее измерение пользователя
        async with async_session() as session:
            result = await session.execute(
                select(FatTracking)
                .where(FatTracking.user_id == message.from_user.id)
                .order_by(desc(FatTracking.created_at))
                .limit(1)
            )
            last_measurement = result.scalar_one_or_none()
        
        if last_measurement:
            text = (
                f"🏃‍♀️ <b>Трекер жировой массы</b>\n\n"
                f"📊 <b>Последнее измерение:</b>\n"
                f"• Дата: {last_measurement.date}\n"
                f"• Процент жира: {last_measurement.body_fat_percent}% {FatPercentageCalculator.get_fat_category(last_measurement.body_fat_percent, last_measurement.gender)['emoji']}\n"
                f"• Категория: {FatPercentageCalculator.get_fat_category(last_measurement.body_fat_percent, last_measurement.gender)['category']}\n"
                f"• Талия: {last_measurement.waist_cm} см\n"
                f"• Бедра: {last_measurement.hip_cm} см\n"
            )
            if last_measurement.goal_fat_percent:
                text += f"• Цель: {last_measurement.goal_fat_percent}%\n"
        else:
            text = (
                f"🏃‍♀️ <b>Трекер жировой массы</b>\n\n"
                f"📈 <b>Отслеживайте процент жира в организме</b>\n\n"
                f"🎯 <b>Возможности:</b>\n"
                f"• Точный расчет по формуле Navy Method\n"
                f"• Установка целей и отслеживание прогресса\n"
                f"• ИИ-рекомендации от Mistral\n"
                f"• История всех измерений\n\n"
                f"📏 <b>Для начала сделайте первое измерение!</b>"
            )
        
        await message.answer(text, reply_markup=fat_tracker_kb, parse_mode='HTML')
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка загрузки меню трекера: {e}\n"
            f"Попробуйте позже.",
            reply_markup=back_kb
        )

@router.callback_query(F.data == 'fat_new_measurement')
async def start_new_measurement(callback: CallbackQuery, state: FSMContext):
    """Начало нового измерения"""
    await callback.answer()
    
    # Получаем данные профиля пользователя
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.tg_id == callback.from_user.id)
        )
        user = result.scalar_one_or_none()
    
    if not user or not user.gender:
        await callback.message.edit_text(
            "❌ <b>Ошибка!</b>\n\n"
            "Для трекера жировой массы необходимо заполнить профиль (особенно пол).\n"
            "Сначала создайте профиль через главное меню.",
            reply_markup=back_kb,
            parse_mode='HTML'
        )
        return
    
    # Нормализуем пол из профиля
    gender_normalized = 'male' if user.gender.lower() in ['м', 'мужской', 'male'] else 'female'
    gender_display = 'Мужской' if gender_normalized == 'male' else 'Женский'
    
    # Сохраняем данные пользователя в состоянии
    await state.update_data(
        user_id=callback.from_user.id,
        gender=gender_normalized,
        height=user.height,
        age=user.age
    )
    
    await state.set_state(FatTracker.waist)
    
    await callback.message.edit_text(
        f"📏 <b>Новое измерение жировой массы</b>\n\n"
        f"👤 Пол: {gender_display}\n\n"
        f"📐 <b>Шаг 1/3:</b> Введите обхват талии в сантиметрах\n\n"
        f"💡 <b>Как измерить:</b>\n"
        f"• Встаньте прямо, дышите нормально\n"
        f"• Измерьте в самой узкой части талии\n"
        f"• Лента должна плотно прилегать, но не давить\n\n"
        f"✏️ <b>Введите число (например: 75.5):</b>",
        reply_markup=back_kb,
        parse_mode='HTML'
    )

@router.message(FatTracker.waist)
async def process_waist(message: Message, state: FSMContext):
    """Обработка ввода обхвата талии"""
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await message.answer("Измерение отменено", reply_markup=fat_tracker_kb)
        return
    
    try:
        waist = float(message.text.replace(',', '.'))
        if waist < 50 or waist > 150:
            await message.answer(
                "❌ Некорректное значение!\nОбхват талии должен быть от 50 до 150 см.",
                reply_markup=back_kb
            )
            return
        
        await state.update_data(waist_cm=waist)
        await state.set_state(FatTracker.hip)
        
        await message.answer(
            f"✅ Талия: {waist} см\n\n"
            f"📐 <b>Шаг 2/3:</b> Введите обхват бедер в сантиметрах\n\n"
            f"💡 <b>Как измерить:</b>\n"
            f"• Встаньте прямо, ноги вместе\n"
            f"• Измерьте в самой широкой части бедер\n"
            f"• Лента должна быть параллельна полу\n\n"
            f"✏️ <b>Введите число (например: 95.0):</b>",
            reply_markup=back_kb,
            parse_mode='HTML'
        )
        
    except ValueError:
        await message.answer(
            "❌ Некорректный формат!\nВведите число (например: 75.5)",
            reply_markup=back_kb
        )

@router.message(FatTracker.hip)
async def process_hip(message: Message, state: FSMContext):
    """Обработка ввода обхвата бедер"""
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await message.answer("Измерение отменено", reply_markup=fat_tracker_kb)
        return
    
    try:
        hip = float(message.text.replace(',', '.'))
        if hip < 60 or hip > 200:
            await message.answer(
                "❌ Некорректное значение!\nОбхват бедер должен быть от 60 до 200 см.",
                reply_markup=back_kb
            )
            return
        
        data = await state.get_data()
        gender = data.get('gender')
        
        await state.update_data(hip_cm=hip)
        
        # Для мужчин запрашиваем обхват шеи для более точного расчета
        if gender == 'male' and data.get('height'):
            await state.set_state(FatTracker.neck)
            await message.answer(
                f"✅ Бедра: {hip} см\n\n"
                f"📐 <b>Шаг 3/4:</b> Введите обхват шеи в сантиметрах\n\n"
                f"💡 <b>Как измерить:</b>\n"
                f"• Измерьте под кадыком\n"
                f"• Лента должна плотно прилегать\n"
                f"• Это повысит точность расчета\n\n"
                f"✏️ <b>Введите число (например: 38.0):</b>\n"
                f"<i>Или нажмите /skip для пропуска</i>",
                reply_markup=back_kb,
                parse_mode='HTML'
            )
        else:
            # Переходим к цели сразу
            await state.set_state(FatTracker.goal)
            await message.answer(
                f"✅ Бедра: {hip} см\n\n"
                f"🎯 <b>Шаг 3/3:</b> Укажите целевой процент жира\n\n"
                f"💡 <b>Рекомендуемые диапазоны:</b>\n"
                f"{'• Мужчины: 10-20% (оптимально 15%)' if gender == 'male' else '• Женщины: 16-25% (оптимально 20%)'}\n\n"
                f"✏️ <b>Введите число (например: 20.0):</b>\n"
                f"<i>Или нажмите /skip для пропуска</i>",
                reply_markup=back_kb,
                parse_mode='HTML'
            )
        
    except ValueError:
        await message.answer(
            "❌ Некорректный формат!\nВведите число (например: 95.0)",
            reply_markup=back_kb
        )

@router.message(FatTracker.neck)
async def process_neck(message: Message, state: FSMContext):
    """Обработка ввода обхвата шеи"""
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await message.answer("Измерение отменено", reply_markup=fat_tracker_kb)
        return
    
    neck = None
    
    if message.text != '/skip':
        try:
            neck = float(message.text.replace(',', '.'))
            if neck < 25 or neck > 50:
                await message.answer(
                    "❌ Некорректное значение!\nОбхват шеи должен быть от 25 до 50 см.",
                    reply_markup=back_kb
                )
                return
        except ValueError:
            await message.answer(
                "❌ Некорректный формат!\nВведите число или /skip",
                reply_markup=back_kb
            )
            return
    
    await state.update_data(neck_cm=neck)
    await state.set_state(FatTracker.goal)
    
    data = await state.get_data()
    gender = data.get('gender')
    
    await message.answer(
        f"✅ Шея: {neck if neck else 'Пропущено'} см\n\n"
        f"🎯 <b>Последний шаг:</b> Укажите целевой процент жира\n\n"
        f"💡 <b>Рекомендуемые диапазоны:</b>\n"
        f"{'• Мужчины: 10-20% (оптимально 15%)' if gender == 'male' else '• Женщины: 16-25% (оптимально 20%)'}\n\n"
        f"✏️ <b>Введите число (например: 18.0):</b>\n"
        f"<i>Или нажмите /skip для пропуска</i>",
        reply_markup=back_kb,
        parse_mode='HTML'
    )

@router.message(FatTracker.goal)
async def process_goal(message: Message, state: FSMContext):
    """Обработка ввода целевого процента жира и расчет результата"""
    if message.text.lower() in ['отмена', 'назад']:
        await state.clear()
        await message.answer("Измерение отменено", reply_markup=fat_tracker_kb)
        return
    
    goal = None
    
    if message.text != '/skip':
        try:
            # Убираем знак % если пользователь его ввел
            goal_text = message.text.replace('%', '').replace(',', '.').strip()
            goal = float(goal_text)
            if goal < 5 or goal > 50:
                await message.answer(
                    "❌ Некорректное значение!\nЦель должна быть от 5 до 50%.",
                    reply_markup=back_kb
                )
                return
        except ValueError:
            await message.answer(
                "❌ Некорректный формат!\nВведите число или /skip",
                reply_markup=back_kb
            )
            return
    
    # Получаем все данные 
    data = await state.get_data()
    
    # Проверяем, устанавливается ли только цель (без измерений)
    if data.get('setting_goal_only'):
        # Только устанавливаем цель без расчетов
        if goal is None:
            await message.answer(
                "❌ Для установки цели нужно ввести число!",
                reply_markup=back_kb
            )
            return
            
        # Обновляем цель в последнем измерении пользователя
        async with async_session() as session:
            result = await session.execute(
                select(FatTracking)
                .where(FatTracking.user_id == message.from_user.id)
                .order_by(desc(FatTracking.created_at))
                .limit(1)
            )
            last_measurement = result.scalar_one_or_none()
            
            if last_measurement:
                last_measurement.goal_fat_percent = goal
                await session.commit()
                
                diff = goal - last_measurement.body_fat_percent
                if abs(diff) <= 1:
                    status = "🎯 Цель достигнута!"
                elif diff > 0:
                    status = f"🎯 До цели: {diff:.1f}% жира"
                else:
                    status = f"🎯 Превышение цели на {abs(diff):.1f}%"
                    
                await message.answer(
                    f"✅ <b>Цель установлена!</b>\n\n"
                    f"🎯 Целевой процент жира: {goal}%\n"
                    f"📊 Текущий: {last_measurement.body_fat_percent}%\n\n"
                    f"{status}",
                    reply_markup=fat_tracker_kb
                )
            else:
                await message.answer(
                    "❌ Сначала сделайте измерение жировой массы!\n"
                    "Нажмите 'Новое измерение' для начала.",
                    reply_markup=fat_tracker_kb
                )
        
        await state.clear()
        return
    
    # Обычный режим с измерениями
    waist_cm = data['waist_cm']
    hip_cm = data['hip_cm']
    neck_cm = data.get('neck_cm')
    height_cm = data.get('height')
    gender = data['gender']
    age = data.get('age')
    
    # Рассчитываем процент жира
    result = FatPercentageCalculator.calculate_fat_percentage(
        waist_cm=waist_cm,
        hip_cm=hip_cm,
        height_cm=height_cm,
        neck_cm=neck_cm,
        gender=gender,
        age=age
    )
    
    if 'error' in result:
        await message.answer(
            f"❌ {result['error']}",
            reply_markup=back_kb
        )
        await state.clear()
        return
    
    # Сохраняем результат в состоянии для последующего сохранения
    await state.update_data(
        goal_fat_percent=goal,
        calculation_result=result
    )
    
    # Формируем отчет
    fat_percent = result['fat_percent']
    category = result['category']
    emoji = result['emoji']
    method = result['method']
    waist_hip_ratio = result['waist_hip_ratio']
    
    text = (
        f"📊 <b>Результаты измерения</b>\n\n"
        f"🏃‍♀️ <b>Процент жира: {fat_percent}%</b> {emoji}\n"
        f"📈 Категория: {category}\n"
        f"📐 Соотношение талия/бедра: {waist_hip_ratio}\n"
        f"🔬 Метод расчета: {method}\n\n"
        f"📏 <b>Измерения:</b>\n"
        f"• Талия: {waist_cm} см\n"
        f"• Бедра: {hip_cm} см\n"
    )
    
    if neck_cm:
        text += f"• Шея: {neck_cm} см\n"
    
    if goal:
        diff = goal - fat_percent
        if abs(diff) <= 1:
            text += f"\n🎯 <b>Цель достигнута!</b> Ваша цель: {goal}%"
        elif diff > 0:
            text += f"\n🎯 До цели ({goal}%): {diff:.1f}% жира"
        else:
            text += f"\n🎯 Превышение цели ({goal}%) на {abs(diff):.1f}%"
    
    text += "\n\n💾 Сохранить это измерение?"
    
    await message.answer(text, reply_markup=fat_confirm_kb, parse_mode='HTML')

@router.callback_query(F.data == 'fat_save')
async def save_measurement(callback: CallbackQuery, state: FSMContext):
    """Сохранение измерения в базу данных"""
    await callback.answer()
    
    try:
        data = await state.get_data()
        result = data['calculation_result']
        
        # Создаем запись в базе данных
        async with async_session() as session:
            fat_record = FatTracking(
                user_id=data['user_id'],
                waist_cm=data['waist_cm'],
                hip_cm=data['hip_cm'],
                neck_cm=data.get('neck_cm'),
                gender=data['gender'],
                body_fat_percent=result['fat_percent'],
                goal_fat_percent=data.get('goal_fat_percent'),
                date=date.today().strftime('%Y-%m-%d')
            )
            session.add(fat_record)
            
            # Синхронизируем данные с профилем пользователя
            user = await session.get(User, data['user_id'])
            if user:
                user.body_fat_percent = result['fat_percent']
                if data.get('goal_fat_percent'):
                    user.goal_fat_percent = data['goal_fat_percent']
            
            await session.commit()
            
            # Также отправляем данные в API для синхронизации
            try:
                import requests
                api_url = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')
                fat_data = {
                    'user_id': data['user_id'],
                    'fat_percent': result['fat_percent'],
                    'goal_fat_percent': data.get('goal_fat_percent')
                }
                requests.post(f'{api_url}/api/fat-data', json=fat_data, timeout=5)
            except:
                pass  # Если API недоступен, продолжаем работу
        
        await state.clear()
        
        await callback.message.edit_text(
            f"✅ <b>Измерение сохранено!</b>\n\n"
            f"📊 Процент жира: {result['fat_percent']}% {result['emoji']}\n"
            f"📅 Дата: {date.today().strftime('%d.%m.%Y')}\n\n"
            f"💡 Хотите получить персональные рекомендации от ИИ?",
            reply_markup=fat_tracker_kb,
            parse_mode='HTML'
        )
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка сохранения: {e}",
            reply_markup=back_kb
        )
        await state.clear()

@router.callback_query(F.data == 'fat_restart')
async def restart_measurement(callback: CallbackQuery, state: FSMContext):
    """Перезапуск измерения"""
    await callback.answer()
    await state.clear()
    await start_new_measurement(callback, state)

@router.callback_query(F.data == 'fat_history')
async def show_fat_history(callback: CallbackQuery):
    """Показ истории измерений"""
    await callback.answer()
    
    try:
        async with async_session() as session:
            result = await session.execute(
                select(FatTracking)
                .where(FatTracking.user_id == callback.from_user.id)
                .order_by(desc(FatTracking.created_at))
                .limit(10)
            )
            measurements = result.scalars().all()
        
        if not measurements:
            await callback.message.edit_text(
                "📊 <b>История измерений</b>\n\n"
                "📈 У вас пока нет сохраненных измерений.\n"
                "Сделайте первое измерение!",
                reply_markup=fat_tracker_kb,
                parse_mode='HTML'
            )
            return
        
        text = "📊 <b>История измерений жира</b>\n\n"
        
        for i, m in enumerate(measurements):
            category = FatPercentageCalculator.get_fat_category(m.body_fat_percent, m.gender)
            text += (
                f"📅 <b>{m.date}</b>\n"
                f"• {m.body_fat_percent}% {category['emoji']}\n"
                f"• Талия: {m.waist_cm} см, Бедра: {m.hip_cm} см\n"
            )
            if m.goal_fat_percent:
                diff = m.goal_fat_percent - m.body_fat_percent
                text += f"• Цель: {m.goal_fat_percent}% ({'достигнута' if abs(diff) <= 1 else f'{diff:+.1f}%'})\n"
            text += "\n"
        
        # Анализ прогресса
        if len(measurements) > 1:
            latest = measurements[0].body_fat_percent
            previous = measurements[1].body_fat_percent
            change = latest - previous
            
            if abs(change) > 0.1:
                text += f"📈 <b>Изменение:</b> {change:+.1f}% с прошлого измерения\n"
        
        await callback.message.edit_text(text, reply_markup=fat_tracker_kb, parse_mode='HTML')
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка загрузки истории: {e}",
            reply_markup=back_kb
        )

@router.callback_query(F.data == 'fat_set_goal')
async def set_fat_goal(callback: CallbackQuery, state: FSMContext):
    """Установка цели по проценту жира"""
    await callback.answer()
    
    # Получаем данные пользователя
    async with async_session() as session:
        user_result = await session.execute(
            select(User).where(User.tg_id == callback.from_user.id)
        )
        user = user_result.scalar_one_or_none()
        
        measurement_result = await session.execute(
            select(FatTracking)
            .where(FatTracking.user_id == callback.from_user.id)
            .order_by(desc(FatTracking.created_at))
            .limit(1)
        )
        last_measurement = measurement_result.scalar_one_or_none()
    
    if not user or not user.gender:
        await callback.message.edit_text(
            "❌ Сначала заполните профиль!",
            reply_markup=back_kb
        )
        return
    
    # Нормализуем пол из профиля
    gender_normalized = 'male' if user.gender.lower() in ['м', 'мужской', 'male'] else 'female'
    
    healthy_range = FatPercentageCalculator.get_healthy_range(gender_normalized, user.age)
    
    text = (
        f"🎯 <b>Установка цели по жиру</b>\n\n"
        f"💡 <b>Рекомендуемые диапазоны:</b>\n"
        f"• Здоровый: {healthy_range['min']}-{healthy_range['max']}%\n"
        f"• Оптимальный: ~{healthy_range['optimal']}%\n\n"
    )
    
    if last_measurement:
        text += f"📊 Текущий уровень: {last_measurement.body_fat_percent}%\n\n"
    
    text += "✏️ <b>Введите целевой процент жира:</b>"
    
    await state.set_state(FatTracker.goal)
    await state.update_data(setting_goal_only=True, user_gender=gender_normalized)
    
    await callback.message.edit_text(text, reply_markup=back_kb, parse_mode='HTML')

@router.callback_query(F.data == 'fat_recommendations')
async def get_fat_recommendations(callback: CallbackQuery):
    """Получение персональных рекомендаций от Mistral AI"""
    await callback.answer()
    
    try:
        # Загружаем данные пользователя
        async with async_session() as session:
            user_result = await session.execute(
                select(User).where(User.tg_id == callback.from_user.id)
            )
            user = user_result.scalar_one_or_none()
            
            measurement_result = await session.execute(
                select(FatTracking)
                .where(FatTracking.user_id == callback.from_user.id)
                .order_by(desc(FatTracking.created_at))
                .limit(5)
            )
            measurements = measurement_result.scalars().all()
        
        if not measurements:
            await callback.message.edit_text(
                "❌ Сначала сделайте измерение жировой массы!",
                reply_markup=fat_tracker_kb
            )
            return
        
        latest = measurements[0]
        
        # Показываем индикатор загрузки
        await callback.message.edit_text(
            "🤖 <b>Генерирую персональные рекомендации...</b>\n\n"
            "⏳ Анализирую ваши данные через ИИ...",
            parse_mode='HTML'
        )
        
        # Импортируем функцию рекомендаций
        from api.ai_api.fat_recommendations import generate_fat_recommendations
        
        # Подготавливаем историю измерений
        history = []
        for m in measurements:
            history.append({
                'fat_percent': m.body_fat_percent,
                'date': datetime.strptime(m.date, '%Y-%m-%d').date(),
                'waist_cm': m.waist_cm,
                'hip_cm': m.hip_cm
            })
        
        # Генерируем рекомендации
        recommendations = await generate_fat_recommendations(
            fat_percent=latest.body_fat_percent,
            goal_fat_percent=latest.goal_fat_percent,
            gender=latest.gender,
            age=user.age if user else None,
            height_cm=user.height if user else None,
            weight_kg=user.weight if user else None,
            activity_level=user.activity_level if user else None,
            waist_cm=latest.waist_cm,
            hip_cm=latest.hip_cm,
            measurement_history=history
        )
        
        # Формируем сообщение с рекомендациями
        text = (
            f"🤖 <b>Персональные рекомендации ИИ</b>\n\n"
            f"📊 <b>Анализ:</b> {recommendations['analysis']}\n\n"
            f"💡 <b>Рекомендации:</b>\n"
            f"{recommendations['recommendations']}\n\n"
            f"🎯 Источник: {('Mistral AI' if recommendations['source'] == 'mistral_ai' else 'Системные')}"
        )
        
        # Сохраняем рекомендацию в базе данных
        async with async_session() as session:
            latest.recommendation = recommendations['recommendations']
            session.add(latest)
            await session.commit()
        
        await callback.message.edit_text(text, reply_markup=fat_tracker_kb, parse_mode='HTML')
        
    except Exception as e:
        await callback.message.edit_text(
            f"❌ Ошибка генерации рекомендаций: {e}\n\n"
            f"Попробуйте позже.",
            reply_markup=fat_tracker_kb
        ) 