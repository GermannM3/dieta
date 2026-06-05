"""REST API для web/mobile клиентов (JWT + WebProfile/WebMeal)."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func

from api.auth_api import get_current_user
from api.ai_api.gigachat_api import generate_text_gigachat
from api.ai_api.fat_calculator import FatPercentageCalculator
from api.motivation_engine import build_daily_motivation, is_conscious_day
from database.init_database import (
    WebUser,
    WebProfile,
    WebMeal,
    WebPreset,
    WebFatTracking,
    async_session,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/web", tags=["web-mobile"])

MAX_CHAT_MESSAGES = 20


def calculate_daily_target(gender: str, age: int, weight: float, height: float, activity_level: float) -> int:
    if gender in ("male", "м"):
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return int(round(bmr * activity_level))


def profile_to_dict(profile: WebProfile) -> dict:
    data = {
        "name": profile.name,
        "gender": profile.gender,
        "age": profile.age,
        "weight": profile.weight,
        "height": profile.height,
        "activity_level": profile.activity_level,
        "daily_target": profile.daily_target,
        "water_target": profile.water_target or 2000,
        "steps_target": profile.steps_target or 10000,
        "mood": profile.mood,
        "water_ml": profile.water_ml or 0,
        "streak_days": profile.streak_days or 0,
        "score": profile.score or 0,
        "is_premium": profile.is_premium or False,
        "body_fat_percent": profile.body_fat_percent,
        "goal_fat_percent": profile.goal_fat_percent,
        "conscious_streak": profile.conscious_streak or 0,
        "longest_streak": profile.longest_streak or 0,
        "total_conscious_days": profile.total_conscious_days or 0,
        "journey_day": _journey_day(profile.journey_start_at),
        "starting_weight": profile.starting_weight,
    }
    if profile.age and profile.weight and profile.height and profile.gender and profile.activity_level:
        data["daily_target"] = profile.daily_target or calculate_daily_target(
            profile.gender, profile.age, profile.weight, profile.height, profile.activity_level
        )
    return data


def _journey_day(journey_start_at) -> int:
    if not journey_start_at:
        return 0
    return max(1, (datetime.utcnow() - journey_start_at).days + 1)


def _normalize_gender(g: str) -> str:
    if g and g.lower() in ("male", "м", "мужской", "m"):
        return "male"
    return "female"


async def get_or_create_profile(session, user_id: int) -> WebProfile:
    result = await session.execute(select(WebProfile).where(WebProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = WebProfile(user_id=user_id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
    return profile


def _build_dietolog_system_prompt(profile: WebProfile, user: WebUser, today_stats: dict) -> str:
    prof = profile_to_dict(profile)
    gender_ru = "мужской" if _normalize_gender(prof.get("gender") or "") == "male" else "женский"
    parts = [
        "Ты персональный диетолог «Твой Диетолог». Обращайся по имени, учитывай профиль и историю.",
        "Отвечай на русском, конкретно, с цифрами и примерами продуктов. Не давай медицинских диагнозов.",
        "",
        "=== ПРОФИЛЬ КЛИЕНТА ===",
        f"Имя: {prof.get('name') or user.name or 'клиент'}",
        f"Пол: {gender_ru}, возраст: {prof.get('age') or '?'}",
        f"Вес: {prof.get('weight') or '?'} кг, рост: {prof.get('height') or '?'} см",
        f"Цель калорий: {prof.get('daily_target') or '?'} ккал/день",
        f"Вода сегодня: {prof.get('water_ml', 0)} / {prof.get('water_target', 2000)} мл",
    ]
    if prof.get("body_fat_percent"):
        parts.append(f"Процент жира: {prof['body_fat_percent']}% (цель: {prof.get('goal_fat_percent') or 'не задана'})")
    if prof.get("conscious_streak"):
        parts.append(f"Серия осознанных дней: {prof['conscious_streak']} (всего {prof.get('total_conscious_days', 0)})")
    if today_stats:
        parts.append(
            f"Сегодня съедено: {today_stats.get('total_calories', 0):.0f} ккал, "
            f"Б{today_stats.get('total_protein', 0):.0f} Ж{today_stats.get('total_fat', 0):.0f} У{today_stats.get('total_carbs', 0):.0f}"
        )
    return "\n".join(parts)


async def _update_streak(session, profile: WebProfile, user_id: int):
    """Обновляет streak при заходе на journey/stats."""
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if profile.last_streak_date == today:
        return

    result = await session.execute(
        select(WebMeal).where(WebMeal.user_id == user_id, WebMeal.date == today)
    )
    meals = result.scalars().all()
    total_cal = sum(m.calories for m in meals)
    target = profile.daily_target

    if is_conscious_day(total_cal, target, len(meals)):
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        if profile.last_streak_date == yesterday:
            profile.conscious_streak = (profile.conscious_streak or 0) + 1
        elif profile.last_streak_date != today:
            profile.conscious_streak = 1
        profile.total_conscious_days = (profile.total_conscious_days or 0) + 1
        profile.longest_streak = max(profile.longest_streak or 0, profile.conscious_streak or 0)
        profile.last_streak_date = today
        if not profile.journey_start_at:
            profile.journey_start_at = datetime.utcnow()
        await session.commit()


class WebProfileUpdate(BaseModel):
    name: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    activity_level: Optional[float] = None
    water_target: Optional[int] = None
    steps_target: Optional[int] = None
    mood: Optional[str] = None
    goal_fat_percent: Optional[float] = None


class WaterUpdate(BaseModel):
    amount_ml: int


class DietologRequest(BaseModel):
    message: str


class FatMeasureRequest(BaseModel):
    waist_cm: float
    hip_cm: float
    neck_cm: Optional[float] = None
    goal_fat_percent: Optional[float] = None


@router.get("/profile")
async def get_web_profile(current_user: WebUser = Depends(get_current_user)):
    async with async_session() as session:
        profile = await get_or_create_profile(session, current_user.id)
        return {"profile": profile_to_dict(profile)}


@router.put("/profile")
async def update_web_profile(
    data: WebProfileUpdate,
    current_user: WebUser = Depends(get_current_user),
):
    async with async_session() as session:
        profile = await get_or_create_profile(session, current_user.id)
        payload = data.model_dump(exclude_unset=True)
        is_first_complete = not profile.journey_start_at
        for key, value in payload.items():
            setattr(profile, key, value)
        if all(getattr(profile, f) for f in ("gender", "age", "weight", "height", "activity_level")):
            profile.daily_target = calculate_daily_target(
                profile.gender, profile.age, profile.weight, profile.height, profile.activity_level
            )
            if is_first_complete and profile.starting_weight is None:
                profile.starting_weight = profile.weight
                profile.journey_start_at = datetime.utcnow()
        profile.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(profile)
        return {"status": "ok", "profile": profile_to_dict(profile)}


@router.get("/journey")
async def get_journey(current_user: WebUser = Depends(get_current_user)):
    """Мотивация дня + streak + недельная статистика."""
    async with async_session() as session:
        profile = await get_or_create_profile(session, current_user.id)
        await _update_streak(session, profile, current_user.id)
        await session.refresh(profile)

        today = datetime.utcnow().strftime("%Y-%m-%d")
        meals_today = await session.execute(
            select(WebMeal).where(WebMeal.user_id == current_user.id, WebMeal.date == today)
        )
        today_list = meals_today.scalars().all()
        today_cal = sum(m.calories for m in today_list)

        week_ago = (datetime.utcnow() - timedelta(days=6)).strftime("%Y-%m-%d")
        week_meals = await session.execute(
            select(WebMeal.date, func.sum(WebMeal.calories).label("cal"))
            .where(WebMeal.user_id == current_user.id, WebMeal.date >= week_ago)
            .group_by(WebMeal.date)
            .order_by(WebMeal.date)
        )
        weekly = [{"date": r.date, "calories": float(r.cal or 0)} for r in week_meals.all()]

        motivation = build_daily_motivation(
            profile.journey_start_at,
            profile.conscious_streak or 0,
            profile.total_conscious_days or 0,
            today_cal,
            profile.daily_target,
            profile.water_ml or 0,
            profile.water_target or 2000,
            profile.body_fat_percent,
            profile.starting_weight,
            profile.weight,
            profile.goal_fat_percent,
        )
        motivation["longest_streak"] = profile.longest_streak or 0

        return {
            "motivation": motivation,
            "weekly_calories": weekly,
            "profile_summary": profile_to_dict(profile),
        }


@router.get("/meals")
async def get_web_meals(
    date: Optional[str] = Query(None),
    current_user: WebUser = Depends(get_current_user),
):
    async with async_session() as session:
        query = select(WebMeal).where(WebMeal.user_id == current_user.id)
        if date:
            query = query.where(WebMeal.date == date)
        query = query.order_by(WebMeal.date.desc(), WebMeal.time.desc())
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


@router.delete("/meals/{meal_id}")
async def delete_web_meal(meal_id: int, current_user: WebUser = Depends(get_current_user)):
    async with async_session() as session:
        result = await session.execute(
            select(WebMeal).where(WebMeal.id == meal_id, WebMeal.user_id == current_user.id)
        )
        meal = result.scalar_one_or_none()
        if not meal:
            raise HTTPException(status_code=404, detail="Приём пищи не найден")
        await session.delete(meal)
        await session.commit()
        return {"status": "ok"}


@router.get("/water")
async def get_web_water(current_user: WebUser = Depends(get_current_user)):
    async with async_session() as session:
        profile = await get_or_create_profile(session, current_user.id)
        return {"water_ml": profile.water_ml or 0, "water_target": profile.water_target or 2000}


@router.post("/water")
async def update_web_water(
    data: WaterUpdate,
    current_user: WebUser = Depends(get_current_user),
):
    async with async_session() as session:
        profile = await get_or_create_profile(session, current_user.id)
        profile.water_ml = max(0, (profile.water_ml or 0) + data.amount_ml)
        await session.commit()
        return {"status": "ok", "total_water": profile.water_ml}


@router.get("/stats")
async def get_web_stats(current_user: WebUser = Depends(get_current_user)):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    async with async_session() as session:
        result = await session.execute(
            select(WebMeal).where(WebMeal.user_id == current_user.id, WebMeal.date == today)
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


@router.post("/fat/measure")
async def measure_body_fat(
    data: FatMeasureRequest,
    current_user: WebUser = Depends(get_current_user),
):
    async with async_session() as session:
        profile = await get_or_create_profile(session, current_user.id)
        if not profile.gender:
            raise HTTPException(status_code=400, detail="Заполните пол в профиле")
        gender = _normalize_gender(profile.gender)
        result = FatPercentageCalculator.calculate_fat_percentage(
            waist_cm=data.waist_cm,
            hip_cm=data.hip_cm,
            height_cm=profile.height,
            neck_cm=data.neck_cm,
            gender=gender,
            age=profile.age,
        )
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])

        fat_pct = result["fat_percent"]
        goal = data.goal_fat_percent or profile.goal_fat_percent
        today = datetime.utcnow().strftime("%Y-%m-%d")

        record = WebFatTracking(
            user_id=current_user.id,
            waist_cm=data.waist_cm,
            hip_cm=data.hip_cm,
            neck_cm=data.neck_cm,
            gender=gender,
            body_fat_percent=fat_pct,
            goal_fat_percent=goal,
            date=today,
        )
        session.add(record)
        profile.body_fat_percent = fat_pct
        if goal:
            profile.goal_fat_percent = goal
        await session.commit()

        return {
            "status": "ok",
            "measurement": {
                **result,
                "goal_fat_percent": goal,
                "date": today,
            },
        }


@router.get("/fat/history")
async def fat_history(
    limit: int = Query(10, le=50),
    current_user: WebUser = Depends(get_current_user),
):
    async with async_session() as session:
        result = await session.execute(
            select(WebFatTracking)
            .where(WebFatTracking.user_id == current_user.id)
            .order_by(WebFatTracking.created_at.desc())
            .limit(limit)
        )
        rows = result.scalars().all()
        return {
            "history": [
                {
                    "id": r.id,
                    "date": r.date,
                    "body_fat_percent": r.body_fat_percent,
                    "goal_fat_percent": r.goal_fat_percent,
                    "waist_cm": r.waist_cm,
                    "hip_cm": r.hip_cm,
                    "neck_cm": r.neck_cm,
                }
                for r in rows
            ]
        }


@router.get("/dietolog/history")
async def dietolog_history(current_user: WebUser = Depends(get_current_user)):
    async with async_session() as session:
        profile = await get_or_create_profile(session, current_user.id)
        return {"history": profile.chat_context or []}


@router.delete("/dietolog/history")
async def clear_dietolog_history(current_user: WebUser = Depends(get_current_user)):
    async with async_session() as session:
        profile = await get_or_create_profile(session, current_user.id)
        profile.chat_context = []
        await session.commit()
        return {"status": "ok"}


@router.post("/dietolog")
async def web_dietolog_chat(
    request: DietologRequest,
    current_user: WebUser = Depends(get_current_user),
):
    async with async_session() as session:
        profile = await get_or_create_profile(session, current_user.id)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        meals_q = await session.execute(
            select(WebMeal).where(WebMeal.user_id == current_user.id, WebMeal.date == today)
        )
        meals = meals_q.scalars().all()
        today_stats = {
            "total_calories": sum(m.calories for m in meals),
            "total_protein": sum(m.protein or 0 for m in meals),
            "total_fat": sum(m.fat or 0 for m in meals),
            "total_carbs": sum(m.carbs or 0 for m in meals),
        }

        system = _build_dietolog_system_prompt(profile, current_user, today_stats)
        history: List[dict] = list(profile.chat_context or [])

        history_text = ""
        for item in history[-10:]:
            role = "Клиент" if item.get("role") == "user" else "Диетолог"
            history_text += f"{role}: {item.get('content', '')}\n"

        prompt = (
            f"{system}\n\n=== ИСТОРИЯ ДИАЛОГА ===\n{history_text}\n"
            f"Клиент: {request.message}\n\nОтвет диетолога:"
        )
        try:
            response = await generate_text_gigachat(prompt)
            history.append({"role": "user", "content": request.message})
            history.append({"role": "assistant", "content": response})
            profile.chat_context = history[-MAX_CHAT_MESSAGES:]
            await session.commit()
            return {"response": response}
        except Exception as e:
            logger.error(f"Ошибка диетолога: {e}")
            raise HTTPException(status_code=500, detail="Ошибка ИИ-диетолога. Попробуйте позже.")


@router.get("/presets")
async def get_web_presets(current_user: WebUser = Depends(get_current_user)):
    async with async_session() as session:
        result = await session.execute(
            select(WebPreset).where(WebPreset.user_id == current_user.id)
        )
        presets = result.scalars().all()
        return {
            "presets": [
                {
                    "id": p.id,
                    "name": p.name,
                    "meal_type": p.meal_type,
                    "food_items": p.food_items,
                    "total_calories": p.total_calories,
                }
                for p in presets
            ]
        }
