"""Сброс дневной нормы воды при смене календарного дня (МСК)."""
from datetime import datetime

import pytz

from database.init_database import User, WebProfile

MOSCOW = pytz.timezone("Europe/Moscow")


def moscow_today() -> str:
    return datetime.now(MOSCOW).strftime("%Y-%m-%d")


def ensure_user_water_today(user: User) -> bool:
    """Сбрасывает water_ml, если наступил новый день. Возвращает True, если был сброс."""
    today = moscow_today()
    data = dict(user.fsm_data or {})
    if data.get("water_date") == today:
        return False
    user.water_ml = 0
    data["water_date"] = today
    user.fsm_data = data
    return True


def ensure_profile_water_today(profile: WebProfile) -> bool:
    today = moscow_today()
    if getattr(profile, "water_date", None) == today:
        return False
    profile.water_ml = 0
    profile.water_date = today
    return True
