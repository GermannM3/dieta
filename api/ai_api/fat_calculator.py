import math
from typing import Optional, Dict, Any

class FatPercentageCalculator:
    """
    Калькулятор процента жира в организме
    Использует различные методы расчета в зависимости от доступных данных
    """
    
    @staticmethod
    def navy_method(waist_cm: float, hip_cm: float, neck_cm: Optional[float], 
                   height_cm: float, gender: str) -> float:
        """
        Navy Method (US Navy) - наиболее точный метод
        
        Args:
            waist_cm: Обхват талии в см
            hip_cm: Обхват бедер в см (только для женщин)
            neck_cm: Обхват шеи в см
            height_cm: Рост в см
            gender: 'male' или 'female'
            
        Returns:
            Процент жира в организме
        """
        if gender.lower() == 'male':
            if neck_cm is None:
                raise ValueError("Для мужчин требуется обхват шеи")
            
            # Формула для мужчин
            body_fat = (86.010 * math.log10(waist_cm - neck_cm) - 
                       70.041 * math.log10(height_cm) + 36.76)
        else:
            # Формула для женщин
            if neck_cm is None:
                # Упрощенная формула без шеи
                body_fat = (163.205 * math.log10(waist_cm + hip_cm) - 
                           97.684 * math.log10(height_cm) - 78.387)
            else:
                body_fat = (163.205 * math.log10(waist_cm + hip_cm - neck_cm) - 
                           97.684 * math.log10(height_cm) - 78.387)
        
        return max(0, min(50, round(body_fat, 1)))
    
    @staticmethod
    def simplified_waist_hip_ratio(waist_cm: float, hip_cm: float, 
                                  gender: str, age: Optional[int] = None) -> float:
        """
        Упрощенный метод на основе соотношения талия/бедра
        Используется когда нет данных о росте и шее
        
        Args:
            waist_cm: Обхват талии в см
            hip_cm: Обхват бедер в см
            gender: 'male' или 'female'
            age: Возраст (опционально для корректировки)
            
        Returns:
            Приблизительный процент жира
        """
        ratio = waist_cm / hip_cm
        
        if gender.lower() == 'male':
            # Формула для мужчин
            if ratio < 0.85:
                base_fat = 10
            elif ratio < 0.90:
                base_fat = 15
            elif ratio < 0.95:
                base_fat = 20
            elif ratio < 1.00:
                base_fat = 25
            else:
                base_fat = 30
        else:
            # Формула для женщин
            if ratio < 0.75:
                base_fat = 15
            elif ratio < 0.80:
                base_fat = 20
            elif ratio < 0.85:
                base_fat = 25
            elif ratio < 0.90:
                base_fat = 30
            else:
                base_fat = 35
        
        # Корректировка по возрасту
        if age:
            if age > 40:
                base_fat += (age - 40) * 0.2
            elif age < 25:
                base_fat -= (25 - age) * 0.1
        
        return max(5, min(45, round(base_fat, 1)))
    
    @staticmethod
    def get_fat_category(fat_percent: float, gender: str, age: Optional[int] = None) -> Dict[str, str]:
        """
        Определяет категорию процента жира
        
        Args:
            fat_percent: Процент жира
            gender: 'male' или 'female'
            age: Возраст
            
        Returns:
            Словарь с категорией и описанием
        """
        if gender.lower() == 'male':
            if fat_percent < 6:
                return {"category": "Очень низкий", "description": "Критически низкий уровень", "emoji": "⚠️"}
            elif fat_percent < 13:
                return {"category": "Атлетический", "description": "Отличная форма", "emoji": "💪"}
            elif fat_percent < 17:
                return {"category": "Хорошая форма", "description": "Здоровый уровень", "emoji": "✅"}
            elif fat_percent < 25:
                return {"category": "Норма", "description": "Приемлемый уровень", "emoji": "👍"}
            else:
                return {"category": "Избыток", "description": "Требует внимания", "emoji": "⚡"}
        else:
            if fat_percent < 16:
                return {"category": "Очень низкий", "description": "Критически низкий уровень", "emoji": "⚠️"}
            elif fat_percent < 20:
                return {"category": "Атлетический", "description": "Отличная форма", "emoji": "💪"}
            elif fat_percent < 25:
                return {"category": "Хорошая форма", "description": "Здоровый уровень", "emoji": "✅"}
            elif fat_percent < 32:
                return {"category": "Норма", "description": "Приемлемый уровень", "emoji": "👍"}
            else:
                return {"category": "Избыток", "description": "Требует внимания", "emoji": "⚡"}
    
    @staticmethod
    def calculate_fat_percentage(waist_cm: float, hip_cm: float, 
                               height_cm: Optional[float] = None,
                               neck_cm: Optional[float] = None,
                               gender: str = 'female',
                               age: Optional[int] = None) -> Dict[str, Any]:
        """
        Основная функция расчета процента жира
        Автоматически выбирает наиболее подходящий метод
        
        Args:
            waist_cm: Обхват талии в см
            hip_cm: Обхват бедер в см
            height_cm: Рост в см (опционально)
            neck_cm: Обхват шеи в см (опционально)
            gender: 'male' или 'female'
            age: Возраст (опционально)
            
        Returns:
            Словарь с результатами расчета
        """
        try:
            # Если есть все данные для Navy Method
            if height_cm and (neck_cm or gender.lower() == 'female'):
                fat_percent = FatPercentageCalculator.navy_method(
                    waist_cm, hip_cm, neck_cm, height_cm, gender
                )
                method = "Navy Method"
                accuracy = "Высокая"
            else:
                # Используем упрощенный метод
                fat_percent = FatPercentageCalculator.simplified_waist_hip_ratio(
                    waist_cm, hip_cm, gender, age
                )
                method = "Соотношение талия/бедра"
                accuracy = "Приблизительная"
            
            # Получаем категорию
            category_info = FatPercentageCalculator.get_fat_category(fat_percent, gender, age)
            
            # Рассчитываем соотношение талия/бедра
            waist_hip_ratio = round(waist_cm / hip_cm, 3)
            
            return {
                "fat_percent": fat_percent,
                "method": method,
                "accuracy": accuracy,
                "category": category_info["category"],
                "description": category_info["description"],
                "emoji": category_info["emoji"],
                "waist_hip_ratio": waist_hip_ratio,
                "measurements": {
                    "waist_cm": waist_cm,
                    "hip_cm": hip_cm,
                    "neck_cm": neck_cm,
                    "height_cm": height_cm
                }
            }
            
        except Exception as e:
            return {
                "error": f"Ошибка расчета: {str(e)}",
                "fat_percent": 0
            }
    
    @staticmethod
    def get_healthy_range(gender: str, age: Optional[int] = None) -> Dict[str, float]:
        """
        Возвращает здоровый диапазон процента жира
        
        Args:
            gender: 'male' или 'female'
            age: Возраст
            
        Returns:
            Словарь с минимальным и максимальным здоровым процентом
        """
        if gender.lower() == 'male':
            if age and age > 40:
                return {"min": 13, "max": 22, "optimal": 17}
            else:
                return {"min": 10, "max": 20, "optimal": 15}
        else:
            if age and age > 40:
                return {"min": 18, "max": 28, "optimal": 23}
            else:
                return {"min": 16, "max": 25, "optimal": 20} 