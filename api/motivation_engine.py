"""Ежедневная мотивация — «Путь осознанного питания» (аналог «Не курю» / «Не пью»)."""

from datetime import datetime
from typing import Optional


# Факты о пользе осознанного питания по дням пути
JOURNEY_MILESTONES = {
    1: ("🌱", "День 1", "Ты начал следить за пищей. Уже сегодня мозг получает сигнал: «я контролирую, а не еда меня»."),
    2: ("💧", "День 2", "На второй день часто появляется привычка пить воду — организм меньше путает жажду с голодом."),
    3: ("⚡", "День 3", "3 дня без хаотичных перекусов — скачки сахара в крови становятся реже, меньше послеобеденной сонливости."),
    5: ("🧠", "День 5", "Через 5 дней осознанного питания легче отличить настоящий голод от привычки «просто съесть»."),
    7: ("🔥", "Неделя", "7 дней под контролем — привычка формируется. Многие замечают, что вечером меньше тянет на сладкое."),
    14: ("😴", "2 недели", "14 дней — часто улучшается сон: тяжёлые ужины перестают будить ночью."),
    21: ("🏆", "3 недели", "21 день — психологи называют это порогом закрепления привычки. Ты на правильном пути."),
    30: ("📉", "Месяц", "30 дней осознанного питания. При дефиците калорий многие теряют 2–4 кг — главное не бросать."),
    60: ("💪", "2 месяца", "60 дней — метаболические привычки закрепляются. Тело «запоминает» новый режим."),
    90: ("👑", "90 дней", "3 месяца — ты прошёл путь, который 80% людей бросают на первой неделе."),
    180: ("🌟", "Полгода", "180 дней осознанного питания — это уже образ жизни, а не диета."),
    365: ("🎉", "Год", "365 дней! Ты доказал себе, что можешь. Это редкость — гордись."),
}

STREAK_BONUSES = {
    3: "3 дня подряд в норме калорий — стабильность важнее идеальности.",
    7: "Неделя без срывов! Так формируется доверие к себе.",
    14: "2 недели streak — ты уже не «на диете», ты живёшь иначе.",
    30: "30 дней streak — это уровень, которого достигают единицы.",
}


def _journey_days(journey_start_at: Optional[datetime]) -> int:
    if not journey_start_at:
        return 0
    delta = datetime.utcnow() - journey_start_at
    return max(1, delta.days + 1)


def _milestone_for_day(day: int) -> Optional[tuple]:
    best = None
    for d, msg in sorted(JOURNEY_MILESTONES.items()):
        if day >= d:
            best = msg
    return best


def build_daily_motivation(
    journey_start_at: Optional[datetime],
    conscious_streak: int,
    total_conscious_days: int,
    today_calories: float,
    daily_target: Optional[float],
    water_ml: int,
    water_target: int,
    body_fat_percent: Optional[float] = None,
    starting_weight: Optional[float] = None,
    current_weight: Optional[float] = None,
    goal_fat_percent: Optional[float] = None,
) -> dict:
    """Собирает карточку дня для экрана «Прогресс»."""
    journey_day = _journey_days(journey_start_at)
    milestone = _milestone_for_day(journey_day)

    lines = []
    if milestone:
        emoji, title, text = milestone
        lines.append({"type": "milestone", "emoji": emoji, "title": title, "text": text})

    if conscious_streak in STREAK_BONUSES:
        lines.append({
            "type": "streak",
            "emoji": "🔥",
            "title": f"Серия {conscious_streak} дней",
            "text": STREAK_BONUSES[conscious_streak],
        })
    elif conscious_streak > 0:
        lines.append({
            "type": "streak",
            "emoji": "🔥",
            "title": f"Серия {conscious_streak} дн.",
            "text": "Каждый день в норме — маленькая победа над старыми привычками.",
        })

    if daily_target and today_calories > 0:
        ratio = today_calories / daily_target
        if ratio <= 1.05:
            lines.append({
                "type": "today",
                "emoji": "✅",
                "title": "Сегодня",
                "text": f"Калории в норме: {today_calories:.0f} из {daily_target:.0f} ккал.",
            })
        elif ratio <= 1.15:
            lines.append({
                "type": "today",
                "emoji": "⚠️",
                "title": "Сегодня",
                "text": f"Немного выше нормы ({today_calories:.0f} ккал). Завтра — новый день.",
            })
        else:
            lines.append({
                "type": "today",
                "emoji": "💡",
                "title": "Сегодня",
                "text": "Перебор калорий — не провал, а данные. Посмотри, что можно скорректировать завтра.",
            })

    if water_target and water_ml >= water_target * 0.8:
        lines.append({
            "type": "water",
            "emoji": "💧",
            "title": "Вода",
            "text": f"Гидратация на уровне: {water_ml} мл. Вода ускоряет обмен веществ на 3–5%.",
        })

    if starting_weight and current_weight and starting_weight > current_weight:
        lost = starting_weight - current_weight
        lines.append({
            "type": "weight",
            "emoji": "📊",
            "title": "Вес",
            "text": f"С начала пути: −{lost:.1f} кг. Медленно — но это устойчивый результат.",
        })

    if body_fat_percent and goal_fat_percent and body_fat_percent > goal_fat_percent:
        diff = body_fat_percent - goal_fat_percent
        lines.append({
            "type": "fat",
            "emoji": "🎯",
            "title": "Жировая масса",
            "text": f"До цели {goal_fat_percent:.1f}% осталось −{diff:.1f} п.п. Регулярные замеры покажут прогресс.",
        })

    if not lines:
        lines.append({
            "type": "welcome",
            "emoji": "🥗",
            "title": "Начни путь",
            "text": "Заполни профиль и добавь первый приём пищи — завтра здесь появится твоя первая мотивация.",
        })

    return {
        "journey_day": journey_day,
        "conscious_streak": conscious_streak,
        "longest_streak": None,  # filled by caller
        "total_conscious_days": total_conscious_days,
        "cards": lines,
    }


def is_conscious_day(total_calories: float, daily_target: Optional[float], meals_count: int) -> bool:
    """День засчитывается в streak, если есть записи и калории в разумных пределах."""
    if meals_count < 1 or not daily_target:
        return False
    ratio = total_calories / daily_target
    return 0.5 <= ratio <= 1.15
