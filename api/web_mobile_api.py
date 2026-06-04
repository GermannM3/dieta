"""REST API для web/mobile клиентов (JWT + WebProfile/WebMeal)."""

import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, delete

from api.auth_api import get_current_user
from api.ai_api.gigachat_api import generate_text_gigachat
from database.init_database import (
    WebUser,
    WebProfile,
    WebMeal,
    WebPreset,
    async_session,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/web", tags=["web-mobile"])


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
    }
    if profile.age and profile.weight and profile.height and profile.gender and profile.activity_level:
        data["daily_target"] = profile.daily_target or calculate_daily_target(
            profile.gender, profile.age, profile.weight, profile.height, profile.activity_level
        )
    return data


async def get_or_create_profile(session, user_id: int) -> WebProfile:
    result = await session.execute(select(WebProfile).where(WebProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = WebProfile(user_id=user_id)
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
    return profile


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


class WaterUpdate(BaseModel):
    amount_ml: int


class DietologRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None


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
        for key, value in payload.items():
            setattr(profile, key, value)
        if all(getattr(profile, f) for f in ("gender", "age", "weight", "height", "activity_level")):
            profile.daily_target = calculate_daily_target(
                profile.gender, profile.age, profile.weight, profile.height, profile.activity_level
            )
        profile.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(profile)
        return {"status": "ok", "profile": profile_to_dict(profile)}


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


@router.post("/dietolog")
async def web_dietolog_chat(
    request: DietologRequest,
    current_user: WebUser = Depends(get_current_user),
):
    async with async_session() as session:
        profile = await get_or_create_profile(session, current_user.id)
        prof = profile_to_dict(profile)
        context = (
            f"Пользователь: {prof.get('name') or current_user.name or 'клиент'}. "
            f"Пол: {prof.get('gender')}, возраст: {prof.get('age')}, "
            f"вес: {prof.get('weight')} кг, рост: {prof.get('height')} см, "
            f"цель калорий: {prof.get('daily_target')} ккал/день.\n"
        )
        history_text = ""
        if request.history:
            for item in request.history[-6:]:
                role = item.get("role", "user")
                content = item.get("content", "")
                history_text += f"{role}: {content}\n"
        prompt = (
            "Ты персональный диетолог. Отвечай кратко, по делу, на русском языке.\n"
            f"{context}\n"
            f"{history_text}\n"
            f"Вопрос пользователя: {request.message}"
        )
        try:
            response = await generate_text_gigachat(prompt)
            return {"response": response}
        except Exception as e:
            logger.error(f"Ошибка диетолога: {e}")
            raise HTTPException(status_code=500, detail="Ошибка ИИ-диетолога. Попробуйте позже.")
