from fastapi.responses import FileResponse
from pathlib import Path
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from database.init_database import Base, engine, User, Meal, Preset, Food, FoodNutrient
import os
import requests
import asyncio
import logging
import signal
from dotenv import load_dotenv
from utils.logger import init_default_logging, get_api_logger, log_exception, log_performance
from api.ai_api.generate_text import translate
import re
from typing import List, Dict, Optional
from food_search_helper import get_search_variants, get_fallback_nutrition, translate_food_name
from api.ai_api.gigachat_api import GigaChatAPI, generate_text_gigachat
from api.ai_api.nutrition_api import NutritionAPI
from datetime import datetime, timedelta
import pytz
from api.auth_api import register_user, login_user, confirm_user, get_current_user, get_current_user_from_token, UserRegister, UserLogin, UserConfirm
from api.web_mobile_api import router as web_mobile_router
from database.crud import update_user_profile
from database.init_database import WebUser, WebProfile, WebMeal, async_session, User
from components.payment_system.payment_operations import check_premium

load_dotenv()

# Инициализация улучшенного логирования
init_default_logging()
logger = get_api_logger()

# Отключаем CalorieNinjas API
# CALORIE_NINJAS_API_KEY = os.getenv("CALORIE_NINJAS_API_KEY")
# if not CALORIE_NINJAS_API_KEY:
#     raise RuntimeError("CALORIE_NINJAS_API_KEY не задан в .env!")
# CALORIE_NINJAS_URL = "https://api.calorieninjas.com/v1/nutrition?query="

app = FastAPI(title="Диетолог API", version="1.0.0")
app.include_router(web_mobile_router)

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

# Флаг для graceful shutdown
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown"""
    logger.info(f"Получен сигнал {signum}, начинаю graceful shutdown API сервера...")
    shutdown_event.set()

# Регистрируем обработчики сигналов
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
if hasattr(signal, 'SIGBREAK'):
    signal.signal(signal.SIGBREAK, signal_handler)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint для Docker"""
    try:
        # Проверяем подключение к базе данных
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/api/health")
async def api_health_check():
    """Health check endpoint для API"""
    try:
        # Проверяем подключение к базе данных
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "connected", "api": "running"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

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
    while not shutdown_event.is_set():
        try:
            await reset_daily_water()
            # Проверяем каждую минуту или до shutdown
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=60)
            except asyncio.TimeoutError:
                pass
        except Exception as e:
            logging.error(f"Ошибка в задаче сброса данных: {e}")
            try:
                await asyncio.wait_for(shutdown_event.wait(), timeout=60)
            except asyncio.TimeoutError:
                pass

@app.on_event("startup")
async def startup_event():
    logging.info("🚀 API сервер запущен!")
    from database.web_migrations import run_web_migrations
    try:
        await run_web_migrations()
    except Exception as e:
        logging.warning(f"Web migrations: {e}")
    asyncio.create_task(daily_reset_task())

@app.on_event("shutdown")
async def shutdown_event_handler():
    logging.info("🛑 API сервер останавливается...")
    shutdown_event.set()
    # Даем время на завершение операций
    await asyncio.sleep(2)
    logging.info("✅ API сервер остановлен")

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
    amount_ml: int

class FatDataIn(BaseModel):
    user_id: int
    fat_percent: float
    goal_fat_percent: Optional[float] = None

class MenuRequest(BaseModel):
    user_id: int
    target_calories: Optional[int] = None

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
    """Добавляет новый шаблон"""
    try:
        async with async_session() as session:
            # Создаем новый шаблон
            new_preset = Preset(
                user_id=preset.user_id,
                name=preset.name,
                food_items=preset.food_items
            )
            session.add(new_preset)
            await session.commit()
            await session.refresh(new_preset)
            
            return {"message": "Шаблон создан", "preset_id": new_preset.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/add_preset_meals")
async def add_preset_meals(data: dict):
    """Добавляет еду из шаблона в прием пищи"""
    try:
        user_id = data.get('user_id')
        preset_id = data.get('preset_id')
        
        if not user_id or not preset_id:
            raise HTTPException(status_code=400, detail="Необходимы user_id и preset_id")
        
        async with async_session() as session:
            # Получаем шаблон
            preset_result = await session.execute(
                select(Preset).where(Preset.id == preset_id, Preset.user_id == user_id)
            )
            preset = preset_result.scalar_one_or_none()
            
            if not preset:
                raise HTTPException(status_code=404, detail="Шаблон не найден")
            
            # Добавляем каждое блюдо из шаблона
            total_calories = 0
            total_protein = 0
            total_fat = 0
            total_carbs = 0
            meals_count = 0
            
            for food_item in preset.food_items:
                food_name = food_item.get('food_name')
                weight = food_item.get('weight', 100)
                
                # Ищем продукт в базе
                food_result = await session.execute(
                    select(Food).where(Food.name.ilike(f"%{food_name}%"))
                )
                food = food_result.scalar_one_or_none()
                
                if food:
                    # Получаем питательные вещества
                    nutrients_result = await session.execute(
                        select(FoodNutrient).where(FoodNutrient.food_id == food.id)
                    )
                    nutrients = nutrients_result.scalars().all()
                    
                    # Рассчитываем калории и БЖУ
                    calories = 0
                    protein = 0
                    fat = 0
                    carbs = 0
                    
                    for nutrient in nutrients:
                        if nutrient.nutrient_name == 'Calories':
                            calories = (nutrient.value * weight) / 100
                        elif nutrient.nutrient_name == 'Protein':
                            protein = (nutrient.value * weight) / 100
                        elif nutrient.nutrient_name == 'Total lipid (fat)':
                            fat = (nutrient.value * weight) / 100
                        elif nutrient.nutrient_name == 'Carbohydrate, by difference':
                            carbs = (nutrient.value * weight) / 100
                    
                    # Создаем запись о приеме пищи
                    meal = Meal(
                        user_id=user_id,
                        food_name=food_name,
                        weight_grams=weight,
                        calories=calories,
                        protein=protein,
                        fat=fat,
                        carbs=carbs,
                        date=datetime.now().date(),
                        time=datetime.now().time()
                    )
                    session.add(meal)
                    
                    total_calories += calories
                    total_protein += protein
                    total_fat += fat
                    total_carbs += carbs
                    meals_count += 1
            
            await session.commit()
            
            return {
                "message": "Еда из шаблона добавлена",
                "preset_name": preset.name,
                "total_calories": total_calories,
                "total_protein": total_protein,
                "total_fat": total_fat,
                "total_carbs": total_carbs,
                "meals_count": meals_count
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@app.post("/api/search_food")
async def search_food(data: dict):
    """Поиск продуктов для веб-приложения"""
    try:
        query = data.get('query', '')
        if not query:
            return {"foods": []}
            
        # Получаем данные о продукте
        nutrition_data = await nutrition_api.get_nutrition_data(query, 100)
        
        return {
            "foods": [
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
        return {"foods": []}

@app.post("/api/calculate_calories")
async def calculate_calories(data: dict):
    """Вычисляет калории для продукта с заданным весом"""
    try:
        food_name = data.get('food_name')
        weight_grams = data.get('weight_grams', 100)
        
        # Получаем данные о калорийности
        nutrition_data = await nutrition_api.get_nutrition_data(food_name, weight_grams)
        
        return {
            "nutrition": {
                "calories": nutrition_data['calories'],
                "protein": nutrition_data['protein'],
                "fat": nutrition_data['fat'],
                "carbs": nutrition_data['carbs']
            },
            "food_name": nutrition_data['food_name'],
            "weight_grams": weight_grams,
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
        user.water_ml = current_water + water.amount_ml
        await session.commit()
        return {"status": "ok", "total_water": user.water_ml}

@app.post("/api/fat-data")
async def save_fat_data(fat_data: FatDataIn):
    """Сохранение данных о жировой массе"""
    try:
        async with async_session() as session:
            user = await session.get(User, fat_data.user_id)
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            
            user.body_fat_percent = fat_data.fat_percent
            if fat_data.goal_fat_percent:
                user.goal_fat_percent = fat_data.goal_fat_percent
            
            await session.commit()
            
            return {
                "status": "ok",
                "body_fat_percent": user.body_fat_percent,
                "goal_fat_percent": user.goal_fat_percent
            }
    except Exception as e:
        logging.error(f"Ошибка сохранения данных о жире: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения данных: {str(e)}")

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
        # menu_items = await generate_meal_suggestions_with_ai(
        #     request.user_id, 
        #     request.meal_type, 
        #     request.target_calories, 
        #     session
        # )
        
        # Временная заглушка для генерации меню
        menu_items = [
            {
                "name": "Овсянка с фруктами",
                "calories": int(request.target_calories * 0.4),
                "protein": 15,
                "fat": 8,
                "carbs": 45
            },
            {
                "name": "Куриная грудка",
                "calories": int(request.target_calories * 0.3),
                "protein": 25,
                "fat": 5,
                "carbs": 0
            },
            {
                "name": "Овощной салат",
                "calories": int(request.target_calories * 0.3),
                "protein": 5,
                "fat": 2,
                "carbs": 15
            }
        ]
        
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


@app.get("/privacy")
async def privacy_policy():
    path = Path(__file__).resolve().parent / "static" / "privacy.html"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Privacy policy not found")
    return FileResponse(path, media_type="text/html; charset=utf-8")

# Добавляем эндпоинты аутентификации
@app.post("/api/auth/register")
async def auth_register(user_data: UserRegister):
    """Регистрация нового пользователя"""
    try:
        result = await register_user(user_data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Ошибка регистрации: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.post("/api/auth/login")
async def auth_login(login_data: UserLogin):
    """Вход пользователя"""
    try:
        result = await login_user(login_data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Ошибка входа: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.post("/api/auth/confirm")
async def auth_confirm(confirmation_data: UserConfirm):
    """Подтверждение email"""
    try:
        result = await confirm_user(confirmation_data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Ошибка подтверждения: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/api/auth/me")
async def auth_me(authorization: str = Header(None)):
    """Получение информации о текущем пользователе"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Токен не предоставлен")
    
    token = authorization.replace("Bearer ", "")
    try:
        user = await get_current_user_from_token(token)
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "is_confirmed": user.is_confirmed,
            "created_at": user.created_at
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Ошибка получения пользователя: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/api/smtp/config")
async def get_smtp_config():
    """Получение примеров конфигурации SMTP"""
    from api.email_service import EmailService
    return {
        "is_configured": EmailService().is_configured,
        "examples": EmailService.get_smtp_config_examples()
    }

# ===== WEB MEALS (JWT) =====

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "germannm@vk.com")

@app.post("/api/web/meals")
async def add_web_meal(meal: dict, current_user: WebUser = Depends(get_current_user)):
    """Добавление приёма пищи для web-пользователя по JWT"""
    required = ["food_name", "weight_grams", "calories"]
    for f in required:
        if f not in meal:
            raise HTTPException(status_code=400, detail=f"Отсутствует поле {f}")
    try:
        async with async_session() as session:
            new_meal = WebMeal(
                user_id=current_user.id,
                date=meal.get("date") or datetime.utcnow().strftime("%Y-%m-%d"),
                time=meal.get("time") or datetime.utcnow().strftime("%H:%M:%S"),
                food_name=meal["food_name"],
                weight_grams=float(meal["weight_grams"]),
                calories=float(meal["calories"]),
                protein=float(meal.get("protein") or 0),
                fat=float(meal.get("fat") or 0),
                carbs=float(meal.get("carbs") or 0),
            )
            session.add(new_meal)
            await session.commit()
            await session.refresh(new_meal)
            return {"status": "ok", "id": new_meal.id}
    except Exception as e:
        logging.error(f"Ошибка добавления web-meal: {e}")
        raise HTTPException(status_code=500, detail="Ошибка добавления приёма пищи")

# ===== АДМИН ПАНЕЛЬ API (по JWT web-пользователя) =====

@app.get("/api/admin/web-users")
async def get_web_users(current_user: WebUser = Depends(get_current_user)):
    """Список web-пользователей (админ по email)"""
    if (current_user.email or "").lower() != ADMIN_EMAIL.lower():
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    async with async_session() as session:
        result = await session.execute(select(WebUser))
        web_users = result.scalars().all()
        return {
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "name": u.name,
                    # признак премиума берём из профиля, если есть
                    "is_premium": False,
                    "created_at": u.created_at.isoformat() if getattr(u, "created_at", None) else None,
                }
                for u in web_users
            ]
        }
 
@app.get("/api/admin/telegram-users")
async def get_telegram_users(current_user: WebUser = Depends(get_current_user)):
    """Получение списка Telegram пользователей для админа"""
    if (current_user.email or "").lower() != ADMIN_EMAIL.lower():
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    async with async_session() as session:
        users_q = await session.execute(select(User).where(User.tg_id.is_not(None)))
        tg_users = users_q.scalars().all()
         
        return {
            "users": [
                {
                    "tg_id": user.tg_id,
                    "name": user.name,
                    "is_premium": user.is_premium,
                    "score": user.score,
                    "streak_days": user.streak_days,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                }
                for user in tg_users
            ]
        }
 
@app.post("/api/admin/toggle-premium")
async def toggle_user_premium(
    request: dict,
    current_user: WebUser = Depends(get_current_user)
):
    """Переключение премиум статуса пользователя"""
    if (current_user.email or "").lower() != ADMIN_EMAIL.lower():
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    user_id = request.get("user_id")
    user_type = request.get("user_type")
    premium = request.get("premium")
    
    if not user_id or user_type not in ["web", "telegram"]:
        raise HTTPException(status_code=400, detail="Неверные параметры")
    
    async with async_session() as session:
        if user_type == "web":
            # Премиум для web-пользователя храним в его профиле
            prof_q = await session.execute(select(WebProfile).where(WebProfile.user_id == int(user_id)))
            profile = prof_q.scalar_one_or_none()
            if not profile:
                # создаём пустой профиль при необходимости
                profile = WebProfile(user_id=int(user_id), is_premium=bool(premium))
                session.add(profile)
            else:
                profile.is_premium = bool(premium)
            await session.commit()
            return {"success": True, "message": f"Премиум {'активирован' if premium else 'деактивирован'}"}
        else:
            user_q = await session.execute(select(User).where(User.tg_id == int(user_id)))
            tgu = user_q.scalar_one_or_none()
            if not tgu:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            tgu.is_premium = bool(premium)
            await session.commit()
            return {"success": True, "message": f"Премиум {'активирован' if premium else 'деактивирован'}"}

# ===== YOOKASSA WEBHOOK =====

@app.post("/api/payment/yookassa/webhook")
async def yookassa_webhook(request: Request):
    """Webhook для получения уведомлений от YooKassa"""
    try:
        # Получаем данные от YooKassa
        data = await request.json()
        logger.info(f"Получен webhook от YooKassa: {data}")
        
        # Проверяем, что это уведомление о платеже
        if data.get("event") == "payment.succeeded":
            payment_id = data["object"]["id"]
            metadata = data["object"].get("metadata", {})
            user_id = int(metadata.get("user_id"))
            subscription_type = metadata.get("subscription_type")
            
            if user_id and subscription_type:
                # Подтверждаем платеж и активируем подписку
                from components.payment_system.payment_operations import PaymentManager
                
                success = await PaymentManager.confirm_payment(payment_id)
                if success:
                    logger.info(f"Подписка активирована для пользователя {user_id}, тип: {subscription_type}")
                    
                    # Обновляем статус пользователя в основной таблице
                    async with async_session() as session:
                        user = await session.execute(
                            select(User).where(User.tg_id == user_id)
                        )
                        user = user.scalar_one_or_none()
                        if user:
                            user.is_premium = True
                            await session.commit()
                            logger.info(f"Пользователь {user_id} получил премиум статус")
                    
                    return {"status": "success", "message": "Payment confirmed and subscription activated"}
                else:
                    logger.error(f"Не удалось подтвердить платеж {payment_id}")
                    return {"status": "error", "message": "Failed to confirm payment"}
            else:
                logger.error(f"Отсутствуют user_id или subscription_type в метаданных: {metadata}")
                return {"status": "error", "message": "Missing user_id or subscription_type"}
        else:
            logger.info(f"Получено уведомление другого типа: {data.get('event')}")
            return {"status": "ignored", "message": "Event type not handled"}
            
    except Exception as e:
        logger.error(f"Ошибка обработки webhook YooKassa: {e}")
        return {"status": "error", "message": str(e)}

# ===== ПЛАТЕЖНЫЕ ENDPOINTS =====

@app.post("/api/payment/create")
async def create_payment(request: Request):
    """Создание платежа через YooKassa"""
    try:
        data = await request.json()
        user_id = data.get("user_id")
        subscription_type = data.get("subscription_type")
        
        if not user_id or not subscription_type:
            raise HTTPException(status_code=400, detail="Missing user_id or subscription_type")
        
        from components.payment_system.payment_operations import PaymentManager
        payment_info = await PaymentManager.create_payment(user_id, subscription_type)
        
        return payment_info
        
    except Exception as e:
        logger.error(f"Ошибка создания платежа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/payment/status/{user_id}")
async def get_payment_status(user_id: int):
    """Получение статуса подписки пользователя"""
    try:
        from components.payment_system.payment_operations import PaymentManager
        
        # Проверяем подписку диетолога
        diet_consultant = await PaymentManager.check_subscription(user_id, 'diet_consultant')
        menu_generator = await PaymentManager.check_subscription(user_id, 'menu_generator')
        
        # Проверяем общий премиум статус
        async with async_session() as session:
            user = await session.execute(
                select(User).where(User.tg_id == user_id)
            )
            user = user.scalar_one_or_none()
            is_premium = user.is_premium if user else False
        
        return {
            "user_id": user_id,
            "is_premium": is_premium,
            "subscriptions": {
                "diet_consultant": diet_consultant,
                "menu_generator": menu_generator
            }
        }
        
    except Exception as e:
        logger.error(f"Ошибка получения статуса платежа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 