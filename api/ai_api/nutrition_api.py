import requests
import os
from typing import Dict, Optional
from .gigachat_api import GigaChatAPI

class NutritionAPI:
    def __init__(self):
        # Отключаем CalorieNinjas API
        # self.api_key = os.getenv('CALORIE_NINJAS_API_KEY')
        # self.base_url = "https://api.calorieninjas.com/v1/nutrition"
        self.gigachat = GigaChatAPI()
    
    async def get_nutrition_data(self, food_name: str, weight_grams: float = 100) -> Dict:
        """
        Получает данные о калорийности продукта через GigaChat.
        """
        # Используем только GigaChat
        return await self.get_nutrition_from_gigachat(food_name, weight_grams)
    
    async def get_nutrition_from_gigachat(self, food_name: str, weight_grams: float) -> Dict:
        """
        Получает данные о калорийности через GigaChat
        """
        try:
            prompt = f"""
            Определи калорийность и БЖУ для продукта: {food_name} весом {weight_grams} грамм.
            
            Ответь в формате JSON:
            {{
                "calories": число_калорий,
                "protein": граммы_белка,
                "fat": граммы_жира,
                "carbs": граммы_углеводов
            }}
            
            Отвечай только JSON, без дополнительного текста.
            """
            
            response = await self.gigachat.generate_text(prompt)
            
            # Пытаемся извлечь JSON из ответа
            import json
            import re
            
            # Ищем JSON в ответе
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                nutrition_data = json.loads(json_str)
                
                # Проверяем валидность данных
                calories = float(nutrition_data.get('calories', 0))
                protein = float(nutrition_data.get('protein', 0))
                fat = float(nutrition_data.get('fat', 0))
                carbs = float(nutrition_data.get('carbs', 0))
                
                # Проверяем, что данные разумные
                if calories > 0 and calories < 10000 and protein >= 0 and fat >= 0 and carbs >= 0:
                    return {
                        'food_name': food_name,
                        'food_name_en': await self.translate_to_english(food_name),
                        'weight_grams': weight_grams,
                        'calories': calories,
                        'protein': protein,
                        'fat': fat,
                        'carbs': carbs,
                        'source': 'gigachat'
                    }
        except Exception as e:
            print(f"Ошибка GigaChat nutrition: {e}")
        
        # Возвращаем базовые данные если ничего не сработало
        return await self.get_fallback_nutrition(food_name, weight_grams)
    
    async def get_fallback_nutrition(self, food_name: str, weight_grams: float) -> Dict:
        """
        Возвращает базовые данные о питании для популярных продуктов
        """
        # Базовые данные для популярных продуктов (на 100г)
        base_nutrition = {
            'яблоко': {'calories': 52, 'protein': 0.3, 'fat': 0.2, 'carbs': 14},
            'банан': {'calories': 89, 'protein': 1.1, 'fat': 0.3, 'carbs': 23},
            'хлеб': {'calories': 265, 'protein': 9, 'fat': 3.2, 'carbs': 49},
            'молоко': {'calories': 42, 'protein': 3.4, 'fat': 1, 'carbs': 5},
            'курица': {'calories': 165, 'protein': 31, 'fat': 3.6, 'carbs': 0},
            'рис': {'calories': 130, 'protein': 2.7, 'fat': 0.3, 'carbs': 28},
            'картофель': {'calories': 77, 'protein': 2, 'fat': 0.1, 'carbs': 17},
            'морковь': {'calories': 41, 'protein': 0.9, 'fat': 0.2, 'carbs': 10},
            'капуста': {'calories': 25, 'protein': 1.3, 'fat': 0.1, 'carbs': 6},
            'лук': {'calories': 40, 'protein': 1.1, 'fat': 0.1, 'carbs': 9},
            'помидор': {'calories': 18, 'protein': 0.9, 'fat': 0.2, 'carbs': 4},
            'огурец': {'calories': 16, 'protein': 0.7, 'fat': 0.1, 'carbs': 4},
            'сыр': {'calories': 113, 'protein': 25, 'fat': 0.3, 'carbs': 1.3},
            'яйцо': {'calories': 155, 'protein': 13, 'fat': 11, 'carbs': 1.1},
            'масло': {'calories': 717, 'protein': 0.9, 'fat': 81, 'carbs': 0.1},
            'сахар': {'calories': 387, 'protein': 0, 'fat': 0, 'carbs': 100},
            'соль': {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0},
            'вода': {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0},
            'чай': {'calories': 1, 'protein': 0, 'fat': 0, 'carbs': 0.2},
            'кофе': {'calories': 2, 'protein': 0.3, 'fat': 0, 'carbs': 0},
            'шаурма': {'calories': 250, 'protein': 15, 'fat': 12, 'carbs': 25},
            'котлета': {'calories': 200, 'protein': 20, 'fat': 12, 'carbs': 5},
            'индейка': {'calories': 135, 'protein': 29, 'fat': 1.7, 'carbs': 0},
            'минералка': {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0},
            'минеральная вода': {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
        }
        
        # Ищем продукт в базовых данных
        food_name_lower = food_name.lower()
        for product, nutrition in base_nutrition.items():
            if product in food_name_lower:
                # Пересчитываем на нужный вес
                multiplier = weight_grams / 100
                return {
                    'food_name': food_name,
                    'food_name_en': food_name,
                    'weight_grams': weight_grams,
                    'calories': round(nutrition['calories'] * multiplier, 1),
                    'protein': round(nutrition['protein'] * multiplier, 1),
                    'fat': round(nutrition['fat'] * multiplier, 1),
                    'carbs': round(nutrition['carbs'] * multiplier, 1),
                    'source': 'fallback_database'
                }
        
        # Если продукт не найден, возвращаем примерные данные
        # Предполагаем, что это обычная еда с умеренной калорийностью
        return {
            'food_name': food_name,
            'food_name_en': food_name,
            'weight_grams': weight_grams,
            'calories': round(100 * weight_grams / 100, 1),  # Примерно 100 ккал на 100г
            'protein': round(5 * weight_grams / 100, 1),     # Примерно 5г белка на 100г
            'fat': round(3 * weight_grams / 100, 1),         # Примерно 3г жира на 100г
            'carbs': round(15 * weight_grams / 100, 1),      # Примерно 15г углеводов на 100г
            'source': 'fallback_estimate'
        }
    
    async def translate_to_english(self, text: str) -> str:
        """
        Переводит текст на английский язык
        """
        try:
            # Простая проверка - если уже на английском, возвращаем как есть
            if text.isascii():
                return text
            
            # Используем GigaChat для перевода
            prompt = f"Переведи на английский язык название продукта: {text}. Ответь только переводом, без дополнительного текста."
            translation = await self.gigachat.generate_text(prompt)
            
            # Очищаем перевод от лишнего текста
            translation = translation.strip().lower()
            
            # Базовые переводы для частых продуктов
            translations = {
                'яблоко': 'apple',
                'банан': 'banana',
                'хлеб': 'bread',
                'молоко': 'milk',
                'мясо': 'meat',
                'курица': 'chicken',
                'рыба': 'fish',
                'рис': 'rice',
                'картофель': 'potato',
                'морковь': 'carrot',
                'капуста': 'cabbage',
                'лук': 'onion',
                'помидор': 'tomato',
                'огурец': 'cucumber',
                'сыр': 'cheese',
                'яйцо': 'egg',
                'масло': 'oil',
                'сахар': 'sugar',
                'соль': 'salt',
                'вода': 'water',
                'чай': 'tea',
                'кофе': 'coffee',
                'шаурма': 'shawarma',
                'котлета': 'cutlet',
                'индейка': 'turkey',
                'минералка': 'mineral water',
                'минеральная вода': 'mineral water'
            }
            
            # Проверяем базовые переводы
            text_lower = text.lower()
            for ru, en in translations.items():
                if ru in text_lower:
                    return en
            
            return translation if translation else text
            
        except Exception as e:
            print(f"Ошибка перевода: {e}")
            return text 