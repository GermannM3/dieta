from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, Column, Integer, BigInteger, String, Float, DateTime, ForeignKey
from database.init_database import Base, engine, User, Meal, Preset, DailyStats
import os
import asyncio
import logging
from dotenv import load_dotenv
from api.ai_api.generate_text import translate, generate_text_with_gigachat
import re
import json
import aiohttp
from typing import Dict, Optional
from datetime import datetime, timedelta
import pytz

# Убираем импорт бота - он будет запускаться отдельно
# from main import main as bot_main

load_dotenv()

app = FastAPI()

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async_session = async_sessionmaker(engine, expire_on_commit=False)

# Кэш для быстрого доступа к данным о продуктах
NUTRITION_CACHE: Dict[str, Dict] = {}

# База данных продуктов для быстрого fallback
COMMON_FOODS = {
    "яблоко": {"calories": 52, "protein": 0.3, "fat": 0.2, "carbs": 14, "fiber": 2.4, "sugar": 10, "sodium": 1},
    "банан": {"calories": 89, "protein": 1.1, "fat": 0.3, "carbs": 23, "fiber": 2.6, "sugar": 12, "sodium": 1},
    "курица": {"calories": 165, "protein": 31, "fat": 3.6, "carbs": 0, "fiber": 0, "sugar": 0, "sodium": 74},
    "рис": {"calories": 130, "protein": 2.7, "fat": 0.3, "carbs": 28, "fiber": 0.4, "sugar": 0.1, "sodium": 1},
    "хлеб": {"calories": 265, "protein": 9, "fat": 3.2, "carbs": 49, "fiber": 2.7, "sugar": 5, "sodium": 491},
    "молоко": {"calories": 42, "protein": 3.4, "fat": 1, "carbs": 5, "fiber": 0, "sugar": 5, "sodium": 44},
    "яйцо": {"calories": 155, "protein": 13, "fat": 11, "carbs": 1.1, "fiber": 0, "sugar": 1.1, "sodium": 124},
    "картофель": {"calories": 77, "protein": 2, "fat": 0.1, "carbs": 17, "fiber": 2.2, "sugar": 0.8, "sodium": 6},
    "морковь": {"calories": 41, "protein": 0.9, "fat": 0.2, "carbs": 10, "fiber": 2.8, "sugar": 4.7, "sodium": 69},
    "огурцы": {"calories": 16, "protein": 0.7, "fat": 0.1, "carbs": 3.6, "fiber": 0.5, "sugar": 1.7, "sodium": 2},
}

def get_moscow_time():
    """Получает текущее время в Москве"""
    moscow_tz = pytz.timezone('Europe/Moscow')
    return datetime.now(moscow_tz)

async def reset_daily_data():
    """Сбрасывает дневные данные в полночь по московскому времени"""
    moscow_time = get_moscow_time()
    
    # Если сейчас полночь (00:00-00:01)
    if moscow_time.hour == 0 and moscow_time.minute <= 1:
        yesterday = (moscow_time - timedelta(days=1)).strftime('%Y-%m-%d')
        
        async with async_session() as session:
            # Получаем всех пользователей
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            for user in users:
                # Сохраняем статистику за вчера
                yesterday_stats = await session.execute(
                    select(Meal).where(Meal.user_id == user.tg_id, Meal.date == yesterday)
                )
                yesterday_meals = yesterday_stats.scalars().all()
                
                total_calories = sum(meal.calories for meal in yesterday_meals)
                total_meals = len(yesterday_meals)
                
                # Сохраняем в daily_stats
                daily_stat = DailyStats(
                    user_id=user.tg_id,
                    date=yesterday,
                    total_calories=total_calories,
                    total_meals=total_meals,
                    water_ml=user.water_ml or 0
                )
                session.add(daily_stat)
                
                # Сбрасываем воду
                user.water_ml = 0
            
            await session.commit()
            logging.info(f"Сброшены дневные данные для {len(users)} пользователей")

@app.on_event("startup")
async def startup_event():
    # Бот запускается отдельно через start_services.py
    logging.info("API сервер запущен!")
    
    # Запускаем фоновую задачу для сброса данных
    asyncio.create_task(daily_reset_task())

async def daily_reset_task():
    """Фоновая задача для сброса данных в полночь"""
    while True:
        try:
            await reset_daily_data()
            # Проверяем каждую минуту
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Ошибка в задаче сброса данных: {e}")
            await asyncio.sleep(60)

class MealIn(BaseModel):
    user_id: int
    food_name: str
    weight_grams: float
    date: str
    time: str

class ProfileIn(BaseModel):
    tg_id: int
    name: str
    age: int
    gender: str
    weight: float
    height: float
    activity_level: int

class PresetIn(BaseModel):
    user_id: int
    name: str
    food_items: list

class WaterIn(BaseModel):
    user_id: int
    ml: int

async def get_nutrition_info_fast(food_name: str, weight_grams: float):
    """Быстрое получение информации о калорийности с кэшированием"""
    
    # Нормализуем название продукта
    food_lower = food_name.lower().strip()
    
    # Проверяем кэш
    if food_lower in NUTRITION_CACHE:
        base_nutrition = NUTRITION_CACHE[food_lower]
    else:
        # Проверяем базу данных продуктов
        if food_lower in COMMON_FOODS:
            base_nutrition = COMMON_FOODS[food_lower]
            NUTRITION_CACHE[food_lower] = base_nutrition
        else:
            # Fallback значения
            base_nutrition = {
                "calories": 100,
                "protein": 5,
                "fat": 2,
                "carbs": 15,
                "fiber": 1,
                "sugar": 2,
                "sodium": 50
            }
            NUTRITION_CACHE[food_lower] = base_nutrition
    
    # Рассчитываем для указанного веса
    ratio = weight_grams / 100  # базовые значения на 100г
    
    return {
        "calories": round(base_nutrition["calories"] * ratio, 1),
        "protein": round(base_nutrition["protein"] * ratio, 1),
        "fat": round(base_nutrition["fat"] * ratio, 1),
        "carbs": round(base_nutrition["carbs"] * ratio, 1),
        "fiber": round(base_nutrition["fiber"] * ratio, 1),
        "sugar": round(base_nutrition["sugar"] * ratio, 1),
        "sodium": round(base_nutrition["sodium"] * ratio, 1)
    }

async def get_nutrition_info(food_name: str, weight_grams: float):
    """Получение информации о калорийности через GigaChat (медленно, но точно)"""
    
    # Сначала пробуем быстрое решение
    fast_result = await get_nutrition_info_fast(food_name, weight_grams)
    
    # Если продукт не найден в базе, используем GigaChat (но с таймаутом)
    food_lower = food_name.lower().strip()
    if food_lower not in COMMON_FOODS:
        try:
            # Устанавливаем таймаут 5 секунд для GigaChat
            prompt = f"""
Ты профессиональный диетолог. Проанализируй продукт и предоставь точную информацию о его пищевой ценности.

Продукт: {food_name}
Вес: {weight_grams} грамм

Пожалуйста, предоставь информацию в следующем JSON формате:
{{
    "calories": число_калорий,
    "protein": белки_в_граммах,
    "fat": жиры_в_граммах,
    "carbs": углеводы_в_граммах,
    "fiber": клетчатка_в_граммах,
    "sugar": сахар_в_граммах,
    "sodium": натрий_в_мг
}}

Учти указанный вес продукта. Отвечай только JSON, без дополнительного текста.
"""

            # Используем asyncio.wait_for для таймаута
            response = await asyncio.wait_for(
                generate_text_with_gigachat(prompt), 
                timeout=5.0
            )
            
            # Пытаемся извлечь JSON из ответа
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                nutrition_data = json.loads(json_match.group())
                
                # Проверяем, что все необходимые поля присутствуют
                required_fields = ['calories', 'protein', 'fat', 'carbs']
                if all(field in nutrition_data and nutrition_data[field] is not None for field in required_fields):
                    # Сохраняем в кэш
                    NUTRITION_CACHE[food_lower] = nutrition_data
                    return nutrition_data
        
        except asyncio.TimeoutError:
            logging.warning(f"Таймаут при получении данных о {food_name}, используем fallback")
        except Exception as e:
            logging.error(f"Ошибка при получении данных о питании: {e}")
    
    return fast_result

@app.post("/api/meal")
async def add_meal(meal: MealIn):
    async with async_session() as session:
        # Используем только быструю базу данных продуктов
        nutrition = await get_nutrition_info_fast(meal.food_name, meal.weight_grams)
        
        new_meal = Meal(
            user_id=meal.user_id,
            food_name=meal.food_name,
            food_name_en=None,  # Пока не используем
            calories=nutrition["calories"],
            protein=nutrition["protein"],
            fat=nutrition["fat"],
            carbs=nutrition["carbs"],
            fiber=nutrition["fiber"],
            sugar=nutrition["sugar"],
            sodium=nutrition["sodium"],
            weight_grams=meal.weight_grams,
            date=meal.date,
            time=meal.time,
            meal_type='other'
        )
        session.add(new_meal)
        await session.commit()
        
        return {
            "status": "ok", 
            "meal_id": new_meal.id, 
            "food_name": meal.food_name,
            "nutrition": nutrition
        }

@app.post("/api/calculate_calories")
async def calculate_calories(food_name: str, weight_grams: float):
    """Отдельный endpoint для расчета калорий"""
    nutrition = await get_nutrition_info(food_name, weight_grams)
    return {
        "food_name": food_name,
        "weight_grams": weight_grams,
        "nutrition": nutrition
    }

@app.post("/api/search_food")
async def search_food(query: str):
    """Поиск продуктов через GigaChat"""
    prompt = f"""
Ты эксперт по продуктам питания. Пользователь ищет: "{query}"

Предложи 5 наиболее подходящих вариантов продуктов в JSON формате:
[
    {{
        "name": "название_продукта",
        "category": "категория",
        "description": "краткое_описание"
    }}
]

Отвечай только JSON, без дополнительного текста.
"""

    try:
        response = await generate_text_with_gigachat(prompt)
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            return {"foods": json.loads(json_match.group())}
        else:
            return {"foods": []}
    except Exception as e:
        logging.error(f"Ошибка при поиске продуктов: {e}")
        return {"foods": []}

@app.post("/api/profile")
async def save_profile(profile: ProfileIn):
    async with async_session() as session:
        user = await session.get(User, profile.tg_id)
        if not user:
            user = User(tg_id=profile.tg_id)
            session.add(user)
        user.name = profile.name
        user.age = profile.age
        user.gender = profile.gender
        user.weight = profile.weight
        user.height = profile.height
        user.activity_level = profile.activity_level
        await session.commit()
        return {"status": "ok"}

@app.get("/api/profile")
async def get_profile(tg_id: int = Query(...)):
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if not user:
            return {"profile": {}}
        return {"profile": {
            "name": user.name,
            "age": user.age,
            "gender": user.gender,
            "weight": user.weight,
            "height": user.height,
            "activity_level": user.activity_level
        }}

@app.get("/api/meals")
async def get_meals(user_id: int = Query(...)):
    async with async_session() as session:
        result = await session.execute(
            select(Meal).where(Meal.user_id == user_id).order_by(Meal.date.desc(), Meal.time.desc())
        )
        meals = result.scalars().all()
        return {"meals": [
            {
                "id": meal.id,
                "food_name": meal.food_name,
                "weight_grams": meal.weight_grams,
                "calories": meal.calories,
                "protein": meal.protein,
                "fat": meal.fat,
                "carbs": meal.carbs,
                "date": meal.date,
                "time": meal.time,
                "meal_type": meal.meal_type
            } for meal in meals
        ]}

@app.get("/api/stats")
async def get_stats(user_id: int = Query(...)):
    """Получение статистики пользователя за сегодня"""
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            return {"stats": {
                "total_calories": 0,
                "total_meals": 0,
                "water_ml": 0,
                "score": 0,
                "streak_days": 0
            }}
        
        # Получаем статистику по приемам пищи за сегодня
        today = get_moscow_time().strftime('%Y-%m-%d')
        result = await session.execute(
            select(Meal).where(Meal.user_id == user_id, Meal.date == today)
        )
        today_meals = result.scalars().all()
        
        total_calories = sum(meal.calories for meal in today_meals)
        total_meals = len(today_meals)
        
        return {"stats": {
            "total_calories": total_calories,
            "total_meals": total_meals,
            "water_ml": user.water_ml or 0,
            "score": user.score or 0,
            "streak_days": user.streak_days or 0
        }}

@app.get("/api/daily_stats")
async def get_daily_stats(user_id: int = Query(...), days: int = Query(7)):
    """Получение детальной статистики по дням"""
    async with async_session() as session:
        # Получаем статистику за последние N дней
        end_date = get_moscow_time().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Получаем сохраненную статистику
        result = await session.execute(
            select(DailyStats).where(
                DailyStats.user_id == user_id,
                DailyStats.date >= start_date.strftime('%Y-%m-%d'),
                DailyStats.date <= end_date.strftime('%Y-%m-%d')
            ).order_by(DailyStats.date.desc())
        )
        daily_stats = result.scalars().all()
        
        # Получаем приемы пищи за эти дни
        meals_result = await session.execute(
            select(Meal).where(
                Meal.user_id == user_id,
                Meal.date >= start_date.strftime('%Y-%m-%d'),
                Meal.date <= end_date.strftime('%Y-%m-%d')
            ).order_by(Meal.date.desc(), Meal.time.desc())
        )
        meals = meals_result.scalars().all()
        
        # Группируем приемы пищи по дням
        meals_by_day = {}
        for meal in meals:
            if meal.date not in meals_by_day:
                meals_by_day[meal.date] = []
            meals_by_day[meal.date].append({
                "food_name": meal.food_name,
                "weight_grams": meal.weight_grams,
                "calories": meal.calories,
                "time": meal.time,
                "meal_type": meal.meal_type
            })
        
        # Формируем результат
        stats_by_day = []
        for stat in daily_stats:
            day_stats = {
                "date": stat.date,
                "total_calories": stat.total_calories,
                "total_meals": stat.total_meals,
                "water_ml": stat.water_ml,
                "mood_score": stat.mood_score,
                "meals": meals_by_day.get(stat.date, [])
            }
            stats_by_day.append(day_stats)
        
        return {"daily_stats": stats_by_day}

@app.get("/api/presets")
async def get_presets(user_id: int = Query(...)):
    async with async_session() as session:
        result = await session.execute(
            select(Preset).where(Preset.user_id == user_id)
        )
        presets = result.scalars().all()
        return {"presets": [
            {
                "id": preset.id,
                "name": preset.name,
                "food_items": preset.food_items
            } for preset in presets
        ]}

@app.post("/api/preset")
async def add_preset(preset: PresetIn):
    async with async_session() as session:
        new_preset = Preset(
            user_id=preset.user_id,
            name=preset.name,
            food_items=preset.food_items
        )
        session.add(new_preset)
        await session.commit()
        return {"status": "ok", "preset_id": new_preset.id}

@app.get("/api/water")
async def get_water(user_id: int = Query(...)):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if not user:
            # Создаем пользователя если не существует
            user = User(tg_id=user_id, water_ml=0)
            session.add(user)
            await session.commit()
        return {"water_ml": user.water_ml or 0}

@app.post("/api/water")
async def add_water(water: WaterIn):
    async with async_session() as session:
        user = await session.get(User, water.user_id)
        if not user:
            # Создаем пользователя если не существует
            user = User(tg_id=water.user_id, water_ml=water.ml)
            session.add(user)
        else:
            # Добавляем к существующему количеству
        user.water_ml = (user.water_ml or 0) + water.ml
        
        await session.commit()
        return {"water_ml": user.water_ml, "added": water.ml} 