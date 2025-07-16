import os
import asyncio
from typing import Dict, Any, Optional
from api.ai_api.generate_text import answer_to_text_prompt

async def generate_fat_recommendations(
    fat_percent: float,
    goal_fat_percent: Optional[float],
    gender: str,
    age: Optional[int],
    height_cm: Optional[float],
    weight_kg: Optional[float],
    activity_level: Optional[int],
    waist_cm: float,
    hip_cm: float,
    measurement_history: Optional[list] = None
) -> Dict[str, Any]:
    """
    Генерирует персональные рекомендации по жировой массе через Mistral AI
    
    Args:
        fat_percent: Текущий процент жира
        goal_fat_percent: Целевой процент жира
        gender: Пол ('male' или 'female')
        age: Возраст
        height_cm: Рост в см
        weight_kg: Вес в кг
        activity_level: Уровень активности (1-5)
        waist_cm: Обхват талии
        hip_cm: Обхват бедер
        measurement_history: История измерений
        
    Returns:
        Словарь с рекомендациями и анализом
    """
    
    try:
        # Определяем категорию жира
        if gender.lower() == 'male':
            if fat_percent < 6:
                category = "критически низкий"
            elif fat_percent < 13:
                category = "атлетический"
            elif fat_percent < 17:
                category = "хорошая форма"
            elif fat_percent < 25:
                category = "норма"
            else:
                category = "избыток"
        else:
            if fat_percent < 16:
                category = "критически низкий"
            elif fat_percent < 20:
                category = "атлетический"
            elif fat_percent < 25:
                category = "хорошая форма"
            elif fat_percent < 32:
                category = "норма"
            else:
                category = "избыток"
        
        # Анализируем прогресс
        progress_info = ""
        if measurement_history and len(measurement_history) > 1:
            recent_change = fat_percent - measurement_history[-2]['fat_percent']
            if recent_change > 0:
                progress_info = f"За последнее время процент жира увеличился на {recent_change:.1f}%. "
            elif recent_change < 0:
                progress_info = f"За последнее время процент жира снизился на {abs(recent_change):.1f}%. "
            else:
                progress_info = "Процент жира остается стабильным. "
        
        # Формируем промпт для Mistral
        gender_ru = "мужчина" if gender.lower() == 'male' else "женщина"
        
        prompt = f"""Ты персональный диетолог-эксперт. Проанализируй данные о жировой массе и дай краткие, персональные рекомендации.

ДАННЫЕ ПОЛЬЗОВАТЕЛЯ:
- Пол: {gender_ru}
- Возраст: {age if age else 'не указан'} лет
- Рост: {height_cm if height_cm else 'не указан'} см
- Вес: {weight_kg if weight_kg else 'не указан'} кг
- Уровень активности: {activity_level if activity_level else 'не указан'}/5
- Текущий % жира: {fat_percent}% (категория: {category})
- Цель: {goal_fat_percent if goal_fat_percent else 'не установлена'}%
- Обхват талии: {waist_cm} см
- Обхват бедер: {hip_cm} см
- Соотношение талия/бедра: {round(waist_cm/hip_cm, 3)}
{progress_info}

ЗАДАЧА:
Дай краткий персональный анализ (2-3 предложения) и 3-4 конкретные рекомендации для достижения здорового процента жира.

ТРЕБОВАНИЯ:
- Ответ до 300 символов
- Конкретные советы по питанию/тренировкам
- Учитывай пол, возраст и цели
- Мотивирующий тон
- Используй эмодзи
"""

        # Получаем ответ от Mistral
        response_text = await answer_to_text_prompt(prompt, 0)
        response = {"text": response_text}
        
        if not response or 'error' in response:
            # Fallback рекомендации
            fallback_recommendations = _get_fallback_recommendations(
                fat_percent, goal_fat_percent, gender, category
            )
            return {
                "recommendations": fallback_recommendations,
                "analysis": f"Ваш процент жира {fat_percent}% относится к категории '{category}'.",
                "source": "system_fallback",
                "category": category
            }
        
        return {
            "recommendations": response['text'],
            "analysis": f"Персональный анализ на основе ваших данных: {fat_percent}% жира, категория '{category}'.",
            "source": "mistral_ai",
            "category": category,
            "tokens_used": response.get('tokens_used', 0)
        }
        
    except Exception as e:
        # В случае ошибки возвращаем базовые рекомендации
        fallback = _get_fallback_recommendations(fat_percent, goal_fat_percent, gender, category)
        return {
            "recommendations": fallback,
            "analysis": f"Ваш процент жира {fat_percent}% (категория: {category})",
            "source": "system_fallback",
            "error": str(e)
        }

def _get_fallback_recommendations(fat_percent: float, goal_fat_percent: Optional[float], 
                                 gender: str, category: str) -> str:
    """Базовые рекомендации без ИИ"""
    
    if category == "избыток":
        return (
            "🔥 Создайте дефицит калорий 300-500 ккал/день\n"
            "💪 Силовые тренировки 3 раза в неделю\n"
            "🏃‍♀️ Кардио 150 минут в неделю\n" 
            "🥗 Больше белка (1.6-2г на кг веса)"
        )
    elif category == "атлетический" or category == "хорошая форма":
        return (
            "✅ Отличный результат! Поддерживайте форму\n"
            "💪 Силовые + кардио тренировки\n"
            "🍎 Сбалансированное питание\n"
            "😴 Качественный сон 7-9 часов"
        )
    elif category == "критически низкий":
        return (
            "⚠️ Слишком низкий % жира опасен для здоровья\n"
            "🍽️ Увеличьте калорийность питания\n"
            "💪 Силовые тренировки для мышечной массы\n"
            "👨‍⚕️ Обратитесь к врачу"
        )
    else:  # норма
        if goal_fat_percent and goal_fat_percent < fat_percent:
            return (
                "🎯 Для достижения цели:\n"
                "🔥 Легкий дефицит калорий 200-300 ккал\n"
                "💪 Силовые тренировки\n"
                "🏃‍♀️ Регулярное кардио"
            )
        else:
            return (
                "👍 Хороший уровень жира! Поддерживайте:\n"
                "🍎 Сбалансированное питание\n"
                "💪 Регулярные тренировки\n"
                "📊 Периодический контроль"
            )

async def generate_quick_tip(fat_percent: float, gender: str) -> str:
    """Быстрый совет на основе процента жира"""
    
    try:
        prompt = f"""Дай один краткий мотивирующий совет для {'мужчины' if gender.lower() == 'male' else 'женщины'} с {fat_percent}% жира. 
        
Ответ должен быть:
- 1 предложение 
- До 80 символов
- С эмодзи
- Мотивирующий"""
        
        response_text = await answer_to_text_prompt(prompt, 0)
        response = {"text": response_text}
        
        if response and 'text' in response:
            return response['text']
        else:
            return "💪 Каждый день - это новый шанс стать лучше!"
            
    except:
        return "🎯 Маленькие шаги ведут к большим результатам!"

async def analyze_fat_progress(measurements_history: list) -> Dict[str, Any]:
    """Анализ прогресса по истории измерений"""
    
    if len(measurements_history) < 2:
        return {"status": "insufficient_data"}
    
    try:
        # Берем данные для анализа
        latest = measurements_history[0]
        previous = measurements_history[1] if len(measurements_history) > 1 else None
        oldest = measurements_history[-1] if len(measurements_history) > 2 else previous
        
        analysis = {
            "total_measurements": len(measurements_history),
            "latest_fat_percent": latest['fat_percent'],
            "measurement_span_days": (latest['date'] - oldest['date']).days if oldest else 0
        }
        
        # Анализ краткосрочного прогресса (последние 2 измерения)
        if previous:
            short_change = latest['fat_percent'] - previous['fat_percent']
            analysis['short_term_change'] = short_change
            analysis['short_term_trend'] = (
                "улучшение" if short_change < -0.5 else
                "ухудшение" if short_change > 0.5 else
                "стабильно"
            )
        
        # Анализ долгосрочного прогресса
        if oldest and oldest != previous:
            long_change = latest['fat_percent'] - oldest['fat_percent']
            analysis['long_term_change'] = long_change
            analysis['long_term_trend'] = (
                "значительное улучшение" if long_change < -2 else
                "улучшение" if long_change < -0.5 else
                "ухудшение" if long_change > 0.5 else
                "стабильно"
            )
        
        # Генерируем рекомендации на основе прогресса
        if analysis.get('short_term_trend') == 'улучшение':
            analysis['motivation'] = "🎉 Отличный прогресс! Продолжайте в том же духе!"
        elif analysis.get('short_term_trend') == 'ухудшение':
            analysis['motivation'] = "💪 Не расстраивайтесь, пересмотрите план питания и тренировок"
        else:
            analysis['motivation'] = "📊 Стабильные показатели - это тоже результат!"
        
        return analysis
        
    except Exception as e:
        return {"status": "error", "error": str(e)} 