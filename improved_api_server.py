from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from database.init_database import Base, engine, User, Meal, Preset, Food, FoodNutrient
import os
import requests
import asyncio
import logging
from dotenv import load_dotenv
from api.ai_api.generate_text import translate
import re
from typing import List, Dict, Optional
from food_search_helper import get_search_variants, get_fallback_nutrition, translate_food_name
from api.ai_api.gigachat_api import GigaChatAPI, generate_text_gigachat
from api.ai_api.nutrition_api import NutritionAPI
from datetime import datetime, timedelta
import pytz

load_dotenv()
# Отключаем CalorieNinjas API
# CALORIE_NINJAS_API_KEY = os.getenv("CALORIE_NINJAS_API_KEY")
# if not CALORIE_NINJAS_API_KEY:
#     raise RuntimeError("CALORIE_NINJAS_API_KEY не задан в .env!")
# CALORIE_NINJAS_URL = "https://api.calorieninjas.com/v1/nutrition?query="

app = FastAPI(title="Диетолог API", version="1.0.0")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем API
gigachat_api = GigaChatAPI()
nutrition_api = NutritionAPI()

# Создаем сессию после инициализации engine
async_session = async_sessionmaker(engine, expire_on_commit=False)

def get_moscow_time():
    """Получает текущее время в Москве"""
    moscow_tz = pytz.timezone('Europe/Moscow')
    return datetime.now(moscow_tz)

async def reset_daily_water():
    """Сбрасывает дневные данные о воде в полночь по московскому времени"""
    moscow_time = get_moscow_time()
    
    # Если сейчас полночь (00:00-00:01)
    if moscow_time.hour == 0 and moscow_time.minute <= 1:
        async with async_session() as session:
            # Получаем всех пользователей и сбрасываем воду
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            for user in users:
                user.water_ml = 0
            
            await session.commit()
            logging.info(f"🔄 Сброшены данные о воде для {len(users)} пользователей в полночь")

async def daily_reset_task():
    """Фоновая задача для сброса данных в полночь"""
    while True:
        try:
            await reset_daily_water()
            # Проверяем каждую минуту
            await asyncio.sleep(60)
        except Exception as e:
            logging.error(f"Ошибка в задаче сброса данных: {e}")
            await asyncio.sleep(60)

@app.on_event("startup")
async def startup_event():
    logging.info("🚀 API сервер запущен!")
    
    # Запускаем фоновую задачу для сброса воды
    asyncio.create_task(daily_reset_task())

# Модели данных
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

class MenuRequest(BaseModel):
    user_id: int
    meal_type: str  # breakfast, lunch, dinner, snack
    target_calories: Optional[int] = None

# Функции для работы с питанием
async def search_food_calorie_ninjas(food_name: str) -> Optional[Dict]:
    """Поиск продукта через CalorieNinjas API"""
    try:
        response = requests.get(
            # CALORIE_NINJAS_URL + food_name,
            # headers={"X-Api-Key": CALORIE_NINJAS_API_KEY},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("items"):
                return data["items"][0]
    except Exception as e:
        logging.error(f"Ошибка CalorieNinjas API: {e}")
    return None

async def search_food_local_db(food_name: str, session: AsyncSession) -> Optional[Dict]:
    """Поиск продукта в локальной базе FoodData Central"""
    try:
        # Поиск по названию в локальной базе
        result = await session.execute(
            text("SELECT fdc_id, description FROM food WHERE LOWER(description) LIKE LOWER(:query) LIMIT 1"),
            {"query": f"%{food_name}%"}
        )
        food_row = result.fetchone()
        
        if food_row:
            fdc_id, description = food_row
            
            # Получаем основные нутриенты (калории, белки, жиры, углеводы)
            nutrient_query = text("""
                SELECT n.amount, n.nutrient_id 
                FROM food_nutrient n 
                WHERE n.fdc_id = :fdc_id 
                AND n.nutrient_id IN (1008, 1003, 1004, 1005)
            """)
            
            nutrients = await session.execute(nutrient_query, {"fdc_id": fdc_id})
            nutrient_data = {row.nutrient_id: row.amount for row in nutrients}
            
            return {
                "name": description,
                "calories": nutrient_data.get(1008, 0),  # Energy
                "protein_g": nutrient_data.get(1003, 0),  # Protein
                "fat_total_g": nutrient_data.get(1004, 0),  # Total lipid (fat)
                "carbohydrates_total_g": nutrient_data.get(1005, 0),  # Carbohydrate
                "serving_size_g": 100  # Стандартная порция 100г
            }
    except Exception as e:
        logging.error(f"Ошибка поиска в локальной базе: {e}")
    return None

async def get_food_nutrition(food_name: str, session: AsyncSession) -> Optional[Dict]:
    """Получение питательности продукта с многоуровневым fallback"""
    # Получаем варианты поиска
    search_variants = get_search_variants(food_name)
    
    # Пробуем каждый вариант в CalorieNinjas
    for variant in search_variants:
        nutrition = await search_food_calorie_ninjas(variant)
        if nutrition:
            return nutrition
    
    # Если не найдено в CalorieNinjas, ищем в локальной базе
    for variant in search_variants:
        nutrition = await search_food_local_db(variant, session)
        if nutrition:
            return nutrition
    
    # Последний fallback - встроенные данные
    return get_fallback_nutrition(food_name)

async def generate_meal_suggestions_with_ai(user_id: int, meal_type: str, target_calories: int, session: AsyncSession) -> List[Dict]:
    """Генерация предложений блюд для меню с использованием AI"""
    try:
        # Получаем профиль пользователя
        user = await session.get(User, user_id)
        user_info = ""
        if user and user.age and user.weight:
            user_info = f"Пользователь: {user.age} лет, вес {user.weight} кг, пол {user.gender or 'не указан'}, активность {user.activity_level or 1}/5"
        
        # Получаем историю питания пользователя
        user_meals = await session.execute(
            select(Meal.food_name).where(Meal.user_id == user_id).distinct().limit(10)
        )
        user_foods = [row[0] for row in user_meals.fetchall()]
        user_history = f"Ранее ел: {', '.join(user_foods[:5])}" if user_foods else "История питания пуста"
        
        # Формируем промпт для AI
        meal_names = {
            'breakfast': 'завтрак',
            'lunch': 'обед', 
            'dinner': 'ужин',
            'snack': 'перекус'
        }
        
        prompt = f"""Создай меню для {meal_names.get(meal_type, 'приёма пищи')} на {target_calories} ккал.
{user_info}
{user_history}

Требования:
1. Предложи 3-5 конкретных блюд/продуктов
2. Укажи примерный вес каждого продукта в граммах
3. Учти сбалансированность БЖУ
4. Используй доступные продукты

Формат ответа (только список, без дополнительного текста):
- Название продукта: вес в граммах
- Название продукта: вес в граммах
...

Пример:
- Овсянка на молоке: 200
- Банан: 100
- Грецкие орехи: 30"""

        # Вызываем AI для генерации меню
        from api.ai_api.gigachat_api import generate_text_gigachat
        ai_response = await generate_text_gigachat(prompt)
        
        # Парсим ответ AI
        menu_items = []
        if ai_response:
            lines = ai_response.strip().split('\n')
            for line in lines:
                if ':' in line and '-' in line:
                    # Убираем "- " в начале
                    clean_line = line.strip().lstrip('- ')
                    if ':' in clean_line:
                        food_name, weight_str = clean_line.split(':', 1)
                        food_name = food_name.strip()
                        
                        # Извлекаем число из строки веса
                        import re
                        weight_match = re.search(r'(\d+)', weight_str.strip())
                        if weight_match:
                            weight = int(weight_match.group(1))
                            
                            # Получаем питательность
                            nutrition = await get_food_nutrition(food_name, session)
                            if nutrition:
                                factor = weight / nutrition["serving_size_g"]
                                menu_items.append({
                                    "name": food_name,
                                    "weight_grams": weight,
                                    "calories": round(nutrition["calories"] * factor),
                                    "protein": round(nutrition.get("protein_g", 0) * factor),
                                    "fat": round(nutrition.get("fat_total_g", 0) * factor),
                                    "carbs": round(nutrition.get("carbohydrates_total_g", 0) * factor)
                                })
        
        # Если AI не сработал, используем fallback
        if not menu_items:
            return await generate_fallback_menu(meal_type, target_calories, session)
        
        return menu_items
        
    except Exception as e:
        logging.error(f"Ошибка генерации меню с AI: {e}")
        return await generate_fallback_menu(meal_type, target_calories, session)

async def generate_fallback_menu(meal_type: str, target_calories: int, session: AsyncSession) -> List[Dict]:
    """Fallback генерация меню без AI"""
    meal_suggestions = {
        "breakfast": ["овсянка", "яйца", "творог", "банан", "хлеб"],
        "lunch": ["курица", "рис", "овощи", "салат", "макароны"],
        "dinner": ["рыба", "гречка", "овощи", "салат", "курица"],
        "snack": ["яблоко", "орехи", "йогурт", "банан", "творог"]
    }
    
    suggestions = meal_suggestions.get(meal_type, meal_suggestions["lunch"])
    menu_items = []
    
    for food_name in suggestions[:4]:
        nutrition = await get_food_nutrition(food_name, session)
        if nutrition:
            if nutrition.get("calories", 0) > 0:
                weight = min(300, max(50, (target_calories // len(suggestions)) * nutrition["serving_size_g"] / nutrition["calories"]))
            else:
                weight = 100
            
            factor = weight / nutrition["serving_size_g"]
            menu_items.append({
                "name": food_name,
                "weight_grams": round(weight),
                "calories": round(nutrition["calories"] * factor),
                "protein": round(nutrition.get("protein_g", 0) * factor),
                "fat": round(nutrition.get("fat_total_g", 0) * factor),
                "carbs": round(nutrition.get("carbohydrates_total_g", 0) * factor)
            })
    
    return menu_items

# API endpoints
@app.post("/api/meal")
async def add_meal(meal: dict):
    """Добавляет прием пищи с калориями от GigaChat"""
    try:
        user_id = meal.get('user_id')
        food_name = meal.get('food_name')
        weight_grams = meal.get('weight_grams', 100)
        date = meal.get('date')
        time = meal.get('time')
        meal_type = meal.get('meal_type', 'other')
        
        # Получаем калории от GigaChat (уже рассчитанные в боте)
        calories = meal.get('calories', 0)
        protein = meal.get('protein', 0)
        fat = meal.get('fat', 0)
        carbs = meal.get('carbs', 0)
        
        # Создаем запись в базе данных
        async with async_session() as session:
            new_meal = Meal(
                user_id=user_id,
                food_name=food_name,
                food_name_en=food_name,  # Используем то же название
                weight_grams=weight_grams,
                calories=calories,
                protein=protein,
                fat=fat,
                carbs=carbs,
                date=date,
                time=time,
                meal_type=meal_type
            )
            session.add(new_meal)
            await session.commit()
            
            # Обновляем счетчик пользователя
            user = await session.get(User, user_id)
            if user:
                user.score = (user.score or 0) + 1
                await session.commit()
        
        return {
            "message": "Прием пищи добавлен",
            "meal": {
                "food_name": food_name,
                "food_name_en": food_name,
                "weight_grams": weight_grams,
                "calories": calories,
                "protein": protein,
                "fat": fat,
                "carbs": carbs,
                "source": "GigaChat"
            }
        }
    except Exception as e:
        print(f"Ошибка добавления приема пищи: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка добавления приема пищи: {str(e)}")

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

@app.put("/api/profile")
async def update_profile(tg_id: int, profile_data: dict):
    """Обновление отдельных полей профиля"""
    try:
        from database.crud import update_user_profile
        success = await update_user_profile(tg_id, profile_data)
        if success:
            return {"status": "ok"}
        else:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
    except Exception as e:
        logging.error(f"Ошибка при обновлении профиля: {e}")
        raise HTTPException(status_code=500, detail="Ошибка обновления профиля")

@app.get("/api/profile")
async def get_profile(tg_id: int = Query(...)):
    try:
        async with async_session() as session:
            user = await session.get(User, tg_id)
            if not user:
                return {"profile": {}}
            
            profile = {
                "name": user.name,
                "age": user.age,
                "gender": user.gender,
                "weight": user.weight,
                "height": user.height,
                "activity_level": user.activity_level,
                "water_ml": user.water_ml,
                "score": user.score,
                "streak_days": user.streak_days
            }
            
            # Рассчитываем BMR и дневную норму калорий, если есть все данные
            if user.age and user.weight and user.height and user.gender:
                # Формула Миффлина-Сан Жеора
                if user.gender == 'м':
                    bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age + 5
                else:
                    bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age - 161
                
                activity_multiplier = 1.2 + (user.activity_level - 1) * 0.3 if user.activity_level else 1.2
                daily_calories = int(bmr * activity_multiplier)
                
                profile["bmr"] = int(bmr)
                profile["daily_calories"] = daily_calories
            
            return {"profile": profile}
    except Exception as e:
        logging.error(f"Ошибка при получении профиля: {e}")
        return {"profile": {}}

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
                "calories": meal.calories,
                "protein": meal.protein,
                "fat": meal.fat,
                "carbs": meal.carbs,
                "weight_grams": meal.weight_grams,
                "date": meal.date,
                "time": meal.time
            } for meal in meals
        ]}

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

@app.get("/api/stats")
async def get_user_stats(user_id: int = Query(...)):
    """Получение статистики пользователя за сегодня"""
    async with async_session() as session:
        try:
            # Статистика за сегодня - используем LIKE для сравнения дат
            today = datetime.now().strftime('%Y-%m-%d')
            result = await session.execute(
                text("""
                    SELECT 
                        SUM(calories) as total_calories,
                        COUNT(*) as total_meals,
                        SUM(protein) as total_protein,
                        SUM(fat) as total_fat,
                        SUM(carbs) as total_carbs
                    FROM meals 
                    WHERE user_id = :user_id 
                    AND date = :today
                """),
                {"user_id": user_id, "today": today}
            )
            
            row = result.fetchone()
            if row:
                return {
                    "stats": {
                        "total_calories": row.total_calories or 0,
                        "total_meals": row.total_meals or 0,
                        "total_protein": row.total_protein or 0,
                        "total_fat": row.total_fat or 0,
                        "total_carbs": row.total_carbs or 0
                    }
                }
            else:
                return {
                    "stats": {
                        "total_calories": 0,
                        "total_meals": 0,
                        "total_protein": 0,
                        "total_fat": 0,
                        "total_carbs": 0
                    }
                }
        except Exception as e:
            logging.error(f"Ошибка при получении статистики: {e}")
            return {
                "stats": {
                    "total_calories": 0,
                    "total_meals": 0,
                    "total_protein": 0,
                    "total_fat": 0,
                    "total_carbs": 0
                }
            }

@app.get("/api/daily_stats")
async def get_daily_stats(user_id: int = Query(...), days: int = Query(7)):
    """Получение статистики по дням"""
    try:
        async with async_session() as session:
            # Статистика по дням - упрощенный запрос без функций даты SQLite
            result = await session.execute(
                text("""
                    SELECT 
                        date,
                        SUM(calories) as total_calories,
                        COUNT(*) as total_meals,
                        SUM(protein) as total_protein,
                        SUM(fat) as total_fat,
                        SUM(carbs) as total_carbs
                    FROM meals 
                    WHERE user_id = :user_id 
                    GROUP BY date
                    ORDER BY date DESC
                    LIMIT :days
                """),
                {"user_id": user_id, "days": days}
            )
            
            daily_stats = []
            for row in result.fetchall():
                daily_stats.append({
                    "date": row.date,
                    "total_calories": row.total_calories or 0,
                    "total_meals": row.total_meals or 0,
                    "total_protein": row.total_protein or 0,
                    "total_fat": row.total_fat or 0,
                    "total_carbs": row.total_carbs or 0
                })
            
            return {"daily_stats": daily_stats}
    except Exception as e:
        logging.error(f"Ошибка при получении статистики: {e}")
        return {"daily_stats": []}

@app.get("/api/search-food")
async def search_food(query: str):
    """Поиск продуктов для веб-приложения"""
    try:
        # Получаем данные о продукте
        nutrition_data = await nutrition_api.get_nutrition_data(query, 100)
        
        return {
            "results": [
                {
                    "name": nutrition_data['food_name'],
                    "name_en": nutrition_data['food_name_en'],
                    "calories_per_100g": nutrition_data['calories'],
                    "protein_per_100g": nutrition_data['protein'],
                    "fat_per_100g": nutrition_data['fat'],
                    "carbs_per_100g": nutrition_data['carbs'],
                    "source": nutrition_data['source']
                }
            ]
        }
    except Exception as e:
        print(f"Ошибка поиска продукта: {e}")
        return {"results": []}

@app.post("/api/calculate-calories")
async def calculate_calories(data: dict):
    """Вычисляет калории для продукта с заданным весом"""
    try:
        food_name = data.get('food_name')
        weight_grams = data.get('weight_grams', 100)
        
        # Получаем данные о калорийности
        nutrition_data = await nutrition_api.get_nutrition_data(food_name, weight_grams)
        
        return {
            "food_name": nutrition_data['food_name'],
            "weight_grams": weight_grams,
            "calories": nutrition_data['calories'],
            "protein": nutrition_data['protein'],
            "fat": nutrition_data['fat'],
            "carbs": nutrition_data['carbs'],
            "source": nutrition_data['source']
        }
    except Exception as e:
        print(f"Ошибка вычисления калорий: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка вычисления калорий: {str(e)}")

@app.get("/api/water")
async def get_water(user_id: int = Query(...)):
    """Получение данных о потреблении воды"""
    async with async_session() as session:
        try:
            user = await session.get(User, user_id)
            if not user:
                return {"water_ml": 0}
            return {"water_ml": getattr(user, 'water_ml', 0) or 0}
        except Exception as e:
            logging.error(f"Ошибка при получении данных о воде: {e}")
            return {"water_ml": 0}

@app.post("/api/water")
async def add_water(water: WaterIn):
    async with async_session() as session:
        user = await session.get(User, water.user_id)
        if not user:
            user = User(tg_id=water.user_id)
            session.add(user)
        
        current_water = getattr(user, 'water_ml', 0) or 0
        user.water_ml = current_water + water.ml
        await session.commit()
        return {"status": "ok", "total_water": user.water_ml}

@app.post("/api/generate-menu")
async def generate_menu(request: MenuRequest):
    """Генерация индивидуального меню"""
    async with async_session() as session:
        user = await session.get(User, request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        # Рассчитываем целевую калорийность, если не указана
        if not request.target_calories:
            if user.age and user.weight and user.height and user.gender:
                # Формула Миффлина-Сан Жеора
                if user.gender == 'м':
                    bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age + 5
                else:
                    bmr = 10 * user.weight + 6.25 * user.height - 5 * user.age - 161
                
                activity_multiplier = 1.2 + (user.activity_level - 1) * 0.3
                target_calories = int(bmr * activity_multiplier)
                
                # Распределяем калории по приёмам пищи
                meal_calories = {
                    "breakfast": int(target_calories * 0.25),
                    "lunch": int(target_calories * 0.35),
                    "dinner": int(target_calories * 0.30),
                    "snack": int(target_calories * 0.10)
                }
                request.target_calories = meal_calories.get(request.meal_type, 500)
            else:
                request.target_calories = 500  # Значение по умолчанию
        
        # Генерируем предложения блюд
        menu_items = await generate_meal_suggestions_with_ai(
            request.user_id, 
            request.meal_type, 
            request.target_calories, 
            session
        )
        
        return {
            "status": "ok",
            "meal_type": request.meal_type,
            "target_calories": request.target_calories,
            "menu_items": menu_items,
            "total_calories": sum(item["calories"] for item in menu_items)
        }

@app.get("/")
async def root():
    return {"message": "Диетолог API работает!", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 