"""REST API для Telegram Mini App (авторизация через initData)."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import select, func

from api.ai_api.fat_calculator import FatPercentageCalculator
from api.ai_api.gigachat_api import generate_text_gigachat
from api.motivation_engine import build_daily_motivation, is_conscious_day
from api.web_mobile_api import calculate_daily_target
from components.access_config import is_free_user
from components.payment_system.payment_operations import (
    PaymentManager,
    get_subscription_price,
    SUBSCRIPTION_DURATION_DAYS,
    SUBSCRIPTION_PRICE_DIET,
    SUBSCRIPTION_PRICE_MENU,
)
from components.telegram_auth import create_tg_token, decode_tg_token, validate_init_data
from components.payment_system.payment_operations import check_premium
from database.init_database import User, Meal, FatTracking, async_session
from utils.daily_water import ensure_user_water_today

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tg", tags=["telegram-mini-app"])
security = HTTPBearer()
MAX_CHAT_MESSAGES = 20


def _mini(user: User) -> dict:
    data = user.fsm_data or {}
    if not isinstance(data, dict):
        data = {}
    mini = data.get("mini_app") or {}
    if not isinstance(mini, dict):
        mini = {}
    return mini


def _set_mini(user: User, patch: dict) -> dict:
    data = dict(user.fsm_data or {})
    mini = dict(_mini(user))
    mini.update(patch)
    data["mini_app"] = mini
    user.fsm_data = data
    return mini


def _normalize_gender(g: str) -> str:
    if g and str(g).lower() in ("male", "м", "мужской", "m"):
        return "male"
    return "female"


def user_to_profile(user: User) -> dict:
    ensure_user_water_today(user)
    mini = _mini(user)
    activity = user.activity_level or 1
    activity_f = 1.2 + (activity - 1) * 0.3 if activity else 1.2
    daily_target = None
    if user.age and user.weight and user.height and user.gender:
        daily_target = calculate_daily_target(
            user.gender if _normalize_gender(user.gender) == "male" else "female",
            user.age,
            user.weight,
            user.height,
            activity_f,
        )
    journey_start = mini.get("journey_start_at")
    journey_day = 0
    if journey_start:
        try:
            start = datetime.fromisoformat(journey_start.replace("Z", ""))
            journey_day = max(1, (datetime.utcnow() - start).days + 1)
        except ValueError:
            journey_day = 1

    return {
        "name": user.name,
        "gender": user.gender,
        "age": user.age,
        "weight": user.weight,
        "height": user.height,
        "activity_level": activity_f,
        "daily_target": daily_target or mini.get("daily_target") or 2000,
        "water_target": mini.get("water_target") or 2000,
        "mood": mini.get("mood"),
        "water_ml": user.water_ml or 0,
        "score": user.score or 0,
        "streak_days": user.streak_days or 0,
        "is_premium": check_premium(user.tg_id),
        "is_free": is_free_user(user.tg_id),
        "body_fat_percent": user.body_fat_percent,
        "goal_fat_percent": user.goal_fat_percent,
        "conscious_streak": mini.get("conscious_streak") or 0,
        "longest_streak": mini.get("longest_streak") or 0,
        "total_conscious_days": mini.get("total_conscious_days") or 0,
        "journey_day": journey_day,
        "starting_weight": mini.get("starting_weight"),
    }


async def get_tg_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    tg_id = decode_tg_token(credentials.credentials)
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if not user:
            user = User(tg_id=tg_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
        elif ensure_user_water_today(user):
            await session.commit()
            await session.refresh(user)
        return user


class AuthRequest(BaseModel):
    init_data: str


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    activity_level: Optional[float] = None
    water_target: Optional[int] = None
    mood: Optional[str] = None
    goal_fat_percent: Optional[float] = None


class MealCreate(BaseModel):
    food_name: str
    weight_grams: float
    calories: float
    protein: Optional[float] = 0
    fat: Optional[float] = 0
    carbs: Optional[float] = 0
    date: Optional[str] = None
    time: Optional[str] = None


class WaterUpdate(BaseModel):
    amount_ml: int


class DietologRequest(BaseModel):
    message: str


class PaymentCreate(BaseModel):
    subscription_type: str


class FatMeasureRequest(BaseModel):
    waist_cm: float
    hip_cm: float
    neck_cm: Optional[float] = None
    goal_fat_percent: Optional[float] = None


@router.post("/auth")
async def tg_auth(body: AuthRequest):
    info = validate_init_data(body.init_data)
    tg_id = info["tg_id"]
    async with async_session() as session:
        user = await session.get(User, tg_id)
        if not user:
            user = User(tg_id=tg_id, name=info.get("first_name"))
            session.add(user)
            await session.commit()
        elif info.get("first_name") and not user.name:
            user.name = info["first_name"]
            await session.commit()

    token = create_tg_token(tg_id)
    return {
        "token": token,
        "user": {
            "tg_id": tg_id,
            "name": info.get("first_name"),
            "username": info.get("username"),
        },
    }


@router.get("/profile")
async def get_profile(user: User = Depends(get_tg_user)):
    return {"profile": user_to_profile(user)}


@router.put("/profile")
async def update_profile(data: ProfileUpdate, user: User = Depends(get_tg_user)):
    async with async_session() as session:
        db_user = await session.get(User, user.tg_id)
        payload = data.model_dump(exclude_unset=True)
        mini_patch = {}
        for key in ("water_target", "mood", "goal_fat_percent"):
            if key in payload:
                mini_patch[key] = payload.pop(key)

        for key, value in payload.items():
            if key == "activity_level" and value is not None:
                # храним как int 1-5 в User.activity_level
                db_user.activity_level = max(1, min(5, int(round(value))))
            elif hasattr(db_user, key) and value is not None:
                setattr(db_user, key, value)

        mini = _mini(db_user)
        if not mini.get("journey_start_at") and db_user.weight and db_user.height and db_user.age:
            mini_patch.setdefault("journey_start_at", datetime.utcnow().isoformat())
            mini_patch.setdefault("starting_weight", db_user.weight)
        if mini_patch:
            _set_mini(db_user, mini_patch)

        await session.commit()
        await session.refresh(db_user)
        return {"status": "ok", "profile": user_to_profile(db_user)}


@router.get("/meals")
async def get_meals(
    date: Optional[str] = Query(None),
    user: User = Depends(get_tg_user),
):
    async with async_session() as session:
        query = select(Meal).where(Meal.user_id == user.tg_id)
        if date:
            query = query.where(Meal.date == date)
        query = query.order_by(Meal.date.desc(), Meal.time.desc())
        result = await session.execute(query)
        meals = result.scalars().all()
        return {
            "meals": [
                {
                    "id": m.id,
                    "food_name": m.food_name,
                    "calories": m.calories,
                    "protein": m.protein,
                    "fat": m.fat,
                    "carbs": m.carbs,
                    "weight_grams": m.weight_grams,
                    "date": m.date,
                    "time": m.time,
                }
                for m in meals
            ]
        }


@router.post("/meals")
async def add_meal(data: MealCreate, user: User = Depends(get_tg_user)):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    now_time = datetime.utcnow().strftime("%H:%M:%S")
    async with async_session() as session:
        meal = Meal(
            user_id=user.tg_id,
            food_name=data.food_name,
            weight_grams=data.weight_grams,
            calories=data.calories,
            protein=data.protein or 0,
            fat=data.fat or 0,
            carbs=data.carbs or 0,
            date=data.date or today,
            time=data.time or now_time,
        )
        session.add(meal)
        db_user = await session.get(User, user.tg_id)
        if db_user:
            db_user.score = (db_user.score or 0) + 1
        await session.commit()
        await session.refresh(meal)
        return {"status": "ok", "meal_id": meal.id}


@router.delete("/meals/{meal_id}")
async def delete_meal(meal_id: int, user: User = Depends(get_tg_user)):
    async with async_session() as session:
        result = await session.execute(
            select(Meal).where(Meal.id == meal_id, Meal.user_id == user.tg_id)
        )
        meal = result.scalar_one_or_none()
        if not meal:
            raise HTTPException(status_code=404, detail="Приём пищи не найден")
        await session.delete(meal)
        await session.commit()
        return {"status": "ok"}


@router.post("/water")
async def update_water(data: WaterUpdate, user: User = Depends(get_tg_user)):
    async with async_session() as session:
        db_user = await session.get(User, user.tg_id)
        ensure_user_water_today(db_user)
        db_user.water_ml = max(0, (db_user.water_ml or 0) + data.amount_ml)
        await session.commit()
        return {"status": "ok", "total_water": db_user.water_ml}


@router.get("/stats")
async def get_stats(user: User = Depends(get_tg_user)):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    async with async_session() as session:
        result = await session.execute(
            select(Meal).where(Meal.user_id == user.tg_id, Meal.date == today)
        )
        meals = result.scalars().all()
        return {
            "stats": {
                "total_calories": sum(m.calories for m in meals),
                "total_protein": sum(m.protein or 0 for m in meals),
                "total_fat": sum(m.fat or 0 for m in meals),
                "total_carbs": sum(m.carbs or 0 for m in meals),
                "total_meals": len(meals),
            }
        }


@router.get("/journey")
async def get_journey(user: User = Depends(get_tg_user)):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    async with async_session() as session:
        db_user = await session.get(User, user.tg_id)
        mini = _mini(db_user)
        prof = user_to_profile(db_user)

        if mini.get("last_streak_date") != today:
            meals_today = await session.execute(
                select(Meal).where(Meal.user_id == user.tg_id, Meal.date == today)
            )
            meals = meals_today.scalars().all()
            total_cal = sum(m.calories for m in meals)
            target = prof.get("daily_target")
            if is_conscious_day(total_cal, target, len(meals)):
                yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
                streak = mini.get("conscious_streak") or 0
                if mini.get("last_streak_date") == yesterday:
                    streak += 1
                else:
                    streak = 1
                mini["conscious_streak"] = streak
                mini["total_conscious_days"] = (mini.get("total_conscious_days") or 0) + 1
                mini["longest_streak"] = max(mini.get("longest_streak") or 0, streak)
                mini["last_streak_date"] = today
                if not mini.get("journey_start_at"):
                    mini["journey_start_at"] = datetime.utcnow().isoformat()
                _set_mini(db_user, mini)
                await session.commit()
                prof = user_to_profile(db_user)

        week_ago = (datetime.utcnow() - timedelta(days=6)).strftime("%Y-%m-%d")
        week_meals = await session.execute(
            select(Meal.date, func.sum(Meal.calories).label("cal"))
            .where(Meal.user_id == user.tg_id, Meal.date >= week_ago)
            .group_by(Meal.date)
            .order_by(Meal.date)
        )
        weekly = [{"date": r.date, "calories": float(r.cal or 0)} for r in week_meals.all()]

        today_meals = await session.execute(
            select(Meal).where(Meal.user_id == user.tg_id, Meal.date == today)
        )
        today_list = today_meals.scalars().all()
        today_cal = sum(m.calories for m in today_list)

        journey_start = None
        if mini.get("journey_start_at"):
            try:
                journey_start = datetime.fromisoformat(mini["journey_start_at"].replace("Z", ""))
            except ValueError:
                pass

        motivation = build_daily_motivation(
            journey_start,
            prof.get("conscious_streak") or 0,
            prof.get("total_conscious_days") or 0,
            today_cal,
            prof.get("daily_target"),
            prof.get("water_ml") or 0,
            prof.get("water_target") or 2000,
            prof.get("body_fat_percent"),
            prof.get("starting_weight"),
            prof.get("weight"),
            prof.get("goal_fat_percent"),
        )
        motivation["longest_streak"] = prof.get("longest_streak") or 0

        return {
            "motivation": motivation,
            "weekly_calories": weekly,
            "profile_summary": prof,
        }


@router.get("/subscriptions")
async def subscriptions(user: User = Depends(get_tg_user)):
    diet = await PaymentManager.check_subscription(user.tg_id, "diet_consultant")
    menu = await PaymentManager.check_subscription(user.tg_id, "menu_generator")
    free = is_free_user(user.tg_id)
    return {
        "is_free": free,
        "is_premium": check_premium(user.tg_id),
        "diet_consultant": diet,
        "menu_generator": menu,
        "prices": {
            "diet_consultant": SUBSCRIPTION_PRICE_DIET,
            "menu_generator": SUBSCRIPTION_PRICE_MENU,
            "duration_days": SUBSCRIPTION_DURATION_DAYS,
        },
    }


@router.post("/payment/create")
async def create_payment(body: PaymentCreate, user: User = Depends(get_tg_user)):
    if body.subscription_type not in ("diet_consultant", "menu_generator"):
        raise HTTPException(status_code=400, detail="Неизвестный тип подписки")
    if is_free_user(user.tg_id):
        return {"free_access": True, "message": "У вас бесплатный доступ"}
    payment = await PaymentManager.create_payment(user.tg_id, body.subscription_type)
    return payment


@router.get("/dietolog/history")
async def dietolog_history(user: User = Depends(get_tg_user)):
    async with async_session() as session:
        db_user = await session.get(User, user.tg_id)
        return {"history": db_user.chat_context or []}


@router.delete("/dietolog/history")
async def clear_dietolog(user: User = Depends(get_tg_user)):
    async with async_session() as session:
        db_user = await session.get(User, user.tg_id)
        db_user.chat_context = []
        await session.commit()
        return {"status": "ok"}


@router.post("/dietolog")
async def dietolog_chat(body: DietologRequest, user: User = Depends(get_tg_user)):
    has_access = await PaymentManager.check_subscription(user.tg_id, "diet_consultant")
    if not has_access:
        raise HTTPException(
            status_code=402,
            detail=f"Нужна подписка «Личный диетолог» ({SUBSCRIPTION_PRICE_DIET}₽/мес)",
        )

    async with async_session() as session:
        db_user = await session.get(User, user.tg_id)
        prof = user_to_profile(db_user)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        meals_q = await session.execute(
            select(Meal).where(Meal.user_id == user.tg_id, Meal.date == today)
        )
        meals = meals_q.scalars().all()
        today_stats = {
            "total_calories": sum(m.calories for m in meals),
            "total_protein": sum(m.protein or 0 for m in meals),
            "total_fat": sum(m.fat or 0 for m in meals),
            "total_carbs": sum(m.carbs or 0 for m in meals),
        }

        gender_ru = "мужской" if _normalize_gender(prof.get("gender") or "") == "male" else "женский"
        system = (
            f"Ты персональный диетолог «Твой Диетолог». Клиент: {prof.get('name') or 'клиент'}. "
            f"Пол {gender_ru}, {prof.get('age')} лет, {prof.get('weight')} кг, рост {prof.get('height')} см. "
            f"Цель {prof.get('daily_target')} ккал. Сегодня: {today_stats['total_calories']:.0f} ккал. "
            "Отвечай на русском, конкретно, без медицинских диагнозов.\n\n"
        )
        history: List[dict] = list(db_user.chat_context or [])
        history_text = ""
        for item in history[-10:]:
            role = "Клиент" if item.get("role") == "user" else "Диетолог"
            history_text += f"{role}: {item.get('content', '')}\n"
        prompt = f"{system}=== ИСТОРИЯ ===\n{history_text}\nКлиент: {body.message}\n\nОтвет:"

        try:
            response = await generate_text_gigachat(prompt)
            history.append({"role": "user", "content": body.message})
            history.append({"role": "assistant", "content": response})
            db_user.chat_context = history[-MAX_CHAT_MESSAGES:]
            await session.commit()
            return {"response": response}
        except Exception as e:
            logger.error(f"Dietolog error: {e}")
            raise HTTPException(status_code=500, detail="Ошибка ИИ-диетолога")


@router.post("/fat/measure")
async def fat_measure(body: FatMeasureRequest, user: User = Depends(get_tg_user)):
    async with async_session() as session:
        db_user = await session.get(User, user.tg_id)
        if not db_user.gender or not db_user.height:
            raise HTTPException(status_code=400, detail="Заполните пол и рост в профиле")
        gender = _normalize_gender(db_user.gender)
        result = FatPercentageCalculator.calculate_fat_percentage(
            waist_cm=body.waist_cm,
            hip_cm=body.hip_cm,
            height_cm=db_user.height,
            neck_cm=body.neck_cm,
            gender=gender,
            age=db_user.age,
        )
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])

        fat_pct = result["fat_percent"]
        goal = body.goal_fat_percent or db_user.goal_fat_percent
        today = datetime.utcnow().strftime("%Y-%m-%d")
        record = FatTracking(
            user_id=user.tg_id,
            waist_cm=body.waist_cm,
            hip_cm=body.hip_cm,
            neck_cm=body.neck_cm,
            gender=gender,
            body_fat_percent=fat_pct,
            goal_fat_percent=goal,
            date=today,
        )
        session.add(record)
        db_user.body_fat_percent = fat_pct
        if goal:
            db_user.goal_fat_percent = goal
        await session.commit()
        return {"status": "ok", "measurement": {**result, "goal_fat_percent": goal, "date": today}}


@router.get("/fat/history")
async def fat_history(limit: int = Query(10, le=50), user: User = Depends(get_tg_user)):
    async with async_session() as session:
        result = await session.execute(
            select(FatTracking)
            .where(FatTracking.user_id == user.tg_id)
            .order_by(FatTracking.created_at.desc())
            .limit(limit)
        )
        rows = result.scalars().all()
        return {
            "history": [
                {
                    "date": r.date,
                    "body_fat_percent": r.body_fat_percent,
                    "goal_fat_percent": r.goal_fat_percent,
                    "waist_cm": r.waist_cm,
                    "hip_cm": r.hip_cm,
                }
                for r in rows
            ]
        }
