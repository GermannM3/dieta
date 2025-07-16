import re
from typing import Dict, Optional

# Словарь переводов популярных продуктов
FOOD_TRANSLATIONS = {
    # Супы
    'борщ': 'borscht soup',
    'суп': 'soup',
    'щи': 'cabbage soup',
    'солянка': 'solyanka soup',
    'харчо': 'kharcho soup',
    'окрошка': 'okroshka soup',
    
    # Каши и крупы
    'каша': 'porridge',
    'овсянка': 'oatmeal',
    'гречка': 'buckwheat',
    'рис': 'rice',
    'пшено': 'millet',
    'манка': 'semolina',
    'перловка': 'pearl barley',
    
    # Мясо и птица
    'говядина': 'beef',
    'свинина': 'pork',
    'курица': 'chicken',
    'индейка': 'turkey',
    'баранина': 'lamb',
    'котлета': 'cutlet',
    'сосиски': 'sausages',
    'колбаса': 'sausage',
    'бефстроганов': 'beef stroganoff',
    
    # Рыба и морепродукты
    'рыба': 'fish',
    'лосось': 'salmon',
    'тунец': 'tuna',
    'селедка': 'herring',
    'карп': 'carp',
    'креветки': 'shrimp',
    'крабы': 'crab',
    
    # Овощи
    'картошка': 'potato',
    'картофель': 'potato',
    'морковь': 'carrot',
    'капуста': 'cabbage',
    'лук': 'onion',
    'чеснок': 'garlic',
    'помидор': 'tomato',
    'огурец': 'cucumber',
    'перец': 'pepper',
    'баклажан': 'eggplant',
    'кабачок': 'zucchini',
    'тыква': 'pumpkin',
    'свекла': 'beetroot',
    'редис': 'radish',
    
    # Фрукты и ягоды
    'яблоко': 'apple',
    'груша': 'pear',
    'банан': 'banana',
    'апельсин': 'orange',
    'лимон': 'lemon',
    'виноград': 'grapes',
    'клубника': 'strawberry',
    'малина': 'raspberry',
    'черника': 'blueberry',
    'вишня': 'cherry',
    'слива': 'plum',
    'персик': 'peach',
    'абрикос': 'apricot',
    'киви': 'kiwi',
    'ананас': 'pineapple',
    'арбуз': 'watermelon',
    'дыня': 'melon',
    
    # Молочные продукты
    'молоко': 'milk',
    'кефир': 'kefir',
    'йогурт': 'yogurt',
    'творог': 'cottage cheese',
    'сметана': 'sour cream',
    'сыр': 'cheese',
    'масло': 'butter',
    'сливки': 'cream',
    'ряженка': 'ryazhenka',
    
    # Хлеб и выпечка
    'хлеб': 'bread',
    'булка': 'bun',
    'батон': 'loaf',
    'лаваш': 'lavash',
    'пирог': 'pie',
    'блины': 'pancakes',
    'оладьи': 'pancakes',
    'сырники': 'cottage cheese pancakes',
    'печенье': 'cookies',
    'торт': 'cake',
    
    # Макароны
    'макароны': 'pasta',
    'спагетти': 'spaghetti',
    'лапша': 'noodles',
    
    # Яйца
    'яйцо': 'egg',
    'яйца': 'eggs',
    'омлет': 'omelet',
    'яичница': 'fried eggs',
    
    # Орехи и семечки
    'орехи': 'nuts',
    'грецкие орехи': 'walnuts',
    'миндаль': 'almonds',
    'фундук': 'hazelnuts',
    'семечки': 'sunflower seeds',
    
    # Напитки
    'чай': 'tea',
    'кофе': 'coffee',
    'сок': 'juice',
    'компот': 'compote',
    'квас': 'kvass',
    'морс': 'berry drink',
    
    # Сладости
    'мед': 'honey',
    'варенье': 'jam',
    'шоколад': 'chocolate',
    'конфеты': 'candy',
    'мороженое': 'ice cream',
    
    # Готовые блюда
    'плов': 'pilaf',
    'пельмени': 'dumplings',
    'вареники': 'vareniki',
    'голубцы': 'stuffed cabbage',
    'манты': 'manti',
    'хинкали': 'khinkali',
    'лагман': 'lagman',
    'шашлык': 'shashlik',
    'гамбургер': 'hamburger',
    'чизбургер': 'cheeseburger',
    'бургер': 'burger',
    'пицца': 'pizza',
    'салат': 'salad',
    'винегрет': 'vinaigrette',
    'оливье': 'olivier salad',
    
    # Дополнительные популярные блюда
    'пельмени': 'dumplings',
    'вареники': 'vareniki',
    'сырники': 'syrniki',
    'блины': 'pancakes',
    'оладьи': 'pancakes',
    'котлеты': 'cutlets',
    'тефтели': 'meatballs',
    'фрикадельки': 'meatballs',
    'жаркое': 'roast',
    'гуляш': 'goulash',
    'рагу': 'stew',
    'запеканка': 'casserole',
    'омлет': 'omelet',
    'яичница': 'scrambled eggs',
    'каша': 'porridge',
    'суп': 'soup',
    'борщ': 'borscht',
    'щи': 'cabbage soup',
    'макароны': 'pasta',
    'спагетти': 'spaghetti',
    'лапша': 'noodles',
    'хлеб': 'bread',
    'булочка': 'bun',
    'бутерброд': 'sandwich',
    'тост': 'toast',
    'сэндвич': 'sandwich',
    'роллы': 'rolls',
    'суши': 'sushi',
    'пирог': 'pie',
    'торт': 'cake',
    'печенье': 'cookies',
    'конфеты': 'candy',
    'шоколад': 'chocolate',
    'мороженое': 'ice cream',
    'йогурт': 'yogurt',
    'кефир': 'kefir',
    'молоко': 'milk',
    'сметана': 'sour cream',
    'масло': 'butter',
    'сыр': 'cheese',
    'колбаса': 'sausage',
    'ветчина': 'ham',
    'бекон': 'bacon',
    'сосиски': 'hot dogs',
    'курица': 'chicken',
    'говядина': 'beef',
    'свинина': 'pork',
    'рыба': 'fish',
    'креветки': 'shrimp',
    'икра': 'caviar',
    'орехи': 'nuts',
    'семечки': 'seeds',
    'чипсы': 'chips',
    'попкорн': 'popcorn',
    'крекеры': 'crackers',
    'печенье': 'cookies',
    'вафли': 'waffles',
    'пряники': 'gingerbread',
    'мармелад': 'marmalade',
    'джем': 'jam',
    'варенье': 'jam',
    'мед': 'honey',
    'сахар': 'sugar',
    'соль': 'salt',
    'специи': 'spices',
    'приправы': 'seasonings',
    'соус': 'sauce',
    'кетчуп': 'ketchup',
    'майонез': 'mayonnaise',
    'горчица': 'mustard',
    'уксус': 'vinegar',
    'масло': 'oil',
}

def translate_food_name(food_name: str) -> str:
    """
    Переводит название продукта с русского на английский
    """
    food_name_lower = food_name.lower().strip()
    
    # Проверяем прямое соответствие
    if food_name_lower in FOOD_TRANSLATIONS:
        return FOOD_TRANSLATIONS[food_name_lower]
    
    # Проверяем частичные соответствия
    for ru_name, en_name in FOOD_TRANSLATIONS.items():
        if ru_name in food_name_lower or food_name_lower in ru_name:
            return en_name
    
    # Если не нашли перевод, возвращаем как есть
    return food_name

def is_russian_text(text: str) -> bool:
    """
    Проверяет, содержит ли текст русские символы
    """
    return bool(re.search(r'[а-яА-ЯёЁ]', text))

def get_search_variants(food_name: str) -> list:
    """
    Возвращает варианты поиска для продукта
    """
    variants = []
    
    # Оригинальное название
    variants.append(food_name.strip())
    
    # Если русский текст, добавляем перевод
    if is_russian_text(food_name):
        translated = translate_food_name(food_name)
        if translated != food_name:
            variants.append(translated)
    
    # Добавляем варианты без лишних слов
    clean_name = food_name.lower()
    for word in ['вареный', 'жареный', 'тушеный', 'запеченный', 'свежий', 'сырой']:
        clean_name = clean_name.replace(word, '').strip()
    
    if clean_name and clean_name != food_name.lower():
        variants.append(clean_name)
        if is_russian_text(clean_name):
            translated_clean = translate_food_name(clean_name)
            if translated_clean not in variants:
                variants.append(translated_clean)
    
    return list(set(variants))  # Убираем дубликаты

# Популярные продукты с калориями (fallback данные)
FALLBACK_NUTRITION = {
    'яблоко': {'calories': 52, 'protein_g': 0.3, 'fat_total_g': 0.2, 'carbohydrates_total_g': 14, 'serving_size_g': 100},
    'банан': {'calories': 89, 'protein_g': 1.1, 'fat_total_g': 0.3, 'carbohydrates_total_g': 23, 'serving_size_g': 100},
    'рис': {'calories': 130, 'protein_g': 2.7, 'fat_total_g': 0.3, 'carbohydrates_total_g': 28, 'serving_size_g': 100},
    'курица': {'calories': 165, 'protein_g': 31, 'fat_total_g': 3.6, 'carbohydrates_total_g': 0, 'serving_size_g': 100},
    'говядина': {'calories': 250, 'protein_g': 26, 'fat_total_g': 15, 'carbohydrates_total_g': 0, 'serving_size_g': 100},
    'картофель': {'calories': 77, 'protein_g': 2, 'fat_total_g': 0.1, 'carbohydrates_total_g': 17, 'serving_size_g': 100},
    'хлеб': {'calories': 265, 'protein_g': 9, 'fat_total_g': 3.2, 'carbohydrates_total_g': 49, 'serving_size_g': 100},
    'молоко': {'calories': 42, 'protein_g': 3.4, 'fat_total_g': 1, 'carbohydrates_total_g': 5, 'serving_size_g': 100},
    'яйцо': {'calories': 155, 'protein_g': 13, 'fat_total_g': 11, 'carbohydrates_total_g': 1.1, 'serving_size_g': 100},
    'творог': {'calories': 98, 'protein_g': 18, 'fat_total_g': 0.6, 'carbohydrates_total_g': 3.3, 'serving_size_g': 100},
    'гречка': {
        'calories': 343,
        'protein_g': 13.2,
        'fat_total_g': 3.4,
        'carbohydrates_total_g': 71.5,
        'serving_size_g': 100
    },
    'рис': {
        'calories': 365,
        'protein_g': 7.1,
        'fat_total_g': 1.0,
        'carbohydrates_total_g': 78.9,
        'serving_size_g': 100
    },
    'овсянка': {
        'calories': 389,
        'protein_g': 16.9,
        'fat_total_g': 6.9,
        'carbohydrates_total_g': 66.3,
        'serving_size_g': 100
    },
    'картошка': {
        'calories': 77,
        'protein_g': 2.0,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 17.5,
        'serving_size_g': 100
    },
    'картофель': {
        'calories': 77,
        'protein_g': 2.0,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 17.5,
        'serving_size_g': 100
    },
    'макароны': {
        'calories': 371,
        'protein_g': 10.4,
        'fat_total_g': 1.1,
        'carbohydrates_total_g': 75.0,
        'serving_size_g': 100
    },
    'хлеб': {
        'calories': 265,
        'protein_g': 9.0,
        'fat_total_g': 3.2,
        'carbohydrates_total_g': 49.8,
        'serving_size_g': 100
    },
    'молоко': {
        'calories': 64,
        'protein_g': 3.2,
        'fat_total_g': 3.6,
        'carbohydrates_total_g': 4.8,
        'serving_size_g': 100
    },
    'творог': {
        'calories': 103,
        'protein_g': 18.0,
        'fat_total_g': 2.0,
        'carbohydrates_total_g': 3.3,
        'serving_size_g': 100
    },
    'сыр': {
        'calories': 363,
        'protein_g': 23.4,
        'fat_total_g': 30.0,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'яйцо': {
        'calories': 157,
        'protein_g': 12.7,
        'fat_total_g': 11.5,
        'carbohydrates_total_g': 0.7,
        'serving_size_g': 100
    },
    'яйца': {
        'calories': 157,
        'protein_g': 12.7,
        'fat_total_g': 11.5,
        'carbohydrates_total_g': 0.7,
        'serving_size_g': 100
    },
    'орехи': {
        'calories': 654,
        'protein_g': 15.2,
        'fat_total_g': 65.2,
        'carbohydrates_total_g': 7.0,
        'serving_size_g': 100
    },
    'йогурт': {
        'calories': 66,
        'protein_g': 5.0,
        'fat_total_g': 3.2,
        'carbohydrates_total_g': 4.1,
        'serving_size_g': 100
    },
    'мясо': {
        'calories': 250,
        'protein_g': 26.0,
        'fat_total_g': 15.0,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'рыба': {
        'calories': 206,
        'protein_g': 22.0,
        'fat_total_g': 12.0,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'борщ': {
        'calories': 49,
        'protein_g': 1.1,
        'fat_total_g': 2.2,
        'carbohydrates_total_g': 6.7,
        'serving_size_g': 100
    },
    'щи': {
        'calories': 32,
        'protein_g': 1.7,
        'fat_total_g': 1.8,
        'carbohydrates_total_g': 2.9,
        'serving_size_g': 100
    },
    'плов': {
        'calories': 198,
        'protein_g': 4.2,
        'fat_total_g': 6.0,
        'carbohydrates_total_g': 32.7,
        'serving_size_g': 100
    },
    'пельмени': {
        'calories': 248,
        'protein_g': 11.9,
        'fat_total_g': 12.4,
        'carbohydrates_total_g': 23.9,
        'serving_size_g': 100
    },
    'вареники': {
        'calories': 221,
        'protein_g': 4.4,
        'fat_total_g': 3.9,
        'carbohydrates_total_g': 43.1,
        'serving_size_g': 100
    },
    'блины': {
        'calories': 233,
        'protein_g': 6.1,
        'fat_total_g': 12.3,
        'carbohydrates_total_g': 26.0,
        'serving_size_g': 100
    },
    'омлет': {
        'calories': 184,
        'protein_g': 9.6,
        'fat_total_g': 15.4,
        'carbohydrates_total_g': 2.1,
        'serving_size_g': 100
    },
    'котлеты': {
        'calories': 221,
        'protein_g': 14.6,
        'fat_total_g': 11.2,
        'carbohydrates_total_g': 13.6,
        'serving_size_g': 100
    },
    'суп': {
        'calories': 30,
        'protein_g': 1.5,
        'fat_total_g': 1.5,
        'carbohydrates_total_g': 3.0,
        'serving_size_g': 100
    },
    'салат': {
        'calories': 15,
        'protein_g': 1.2,
        'fat_total_g': 0.2,
        'carbohydrates_total_g': 2.8,
        'serving_size_g': 100
    },
    'каша': {
        'calories': 90,
        'protein_g': 3.0,
        'fat_total_g': 1.0,
        'carbohydrates_total_g': 17.0,
        'serving_size_g': 100
    },
    'бутерброд': {
        'calories': 282,
        'protein_g': 12.0,
        'fat_total_g': 12.0,
        'carbohydrates_total_g': 30.0,
        'serving_size_g': 100
    },
    'пицца': {
        'calories': 266,
        'protein_g': 11.0,
        'fat_total_g': 10.4,
        'carbohydrates_total_g': 33.0,
        'serving_size_g': 100
    },
    'гамбургер': {
        'calories': 295,
        'protein_g': 17.0,
        'fat_total_g': 14.0,
        'carbohydrates_total_g': 24.0,
        'serving_size_g': 100
    },
    'чизбургер': {
        'calories': 535,
        'protein_g': 25.2,
        'fat_total_g': 31.0,
        'carbohydrates_total_g': 40.0,
        'serving_size_g': 100
    },
    'бургер': {
        'calories': 295,
        'protein_g': 17.0,
        'fat_total_g': 14.0,
        'carbohydrates_total_g': 24.0,
        'serving_size_g': 100
    },
    'сосиски': {
        'calories': 266,
        'protein_g': 10.1,
        'fat_total_g': 23.9,
        'carbohydrates_total_g': 1.6,
        'serving_size_g': 100
    },
    'колбаса': {
        'calories': 301,
        'protein_g': 12.2,
        'fat_total_g': 27.5,
        'carbohydrates_total_g': 1.5,
        'serving_size_g': 100
    },
    'шоколад': {
        'calories': 534,
        'protein_g': 5.4,
        'fat_total_g': 31.0,
        'carbohydrates_total_g': 60.3,
        'serving_size_g': 100
    },
    'мороженое': {
        'calories': 207,
        'protein_g': 3.7,
        'fat_total_g': 11.0,
        'carbohydrates_total_g': 24.4,
        'serving_size_g': 100
    },
    'торт': {
        'calories': 344,
        'protein_g': 4.4,
        'fat_total_g': 15.0,
        'carbohydrates_total_g': 51.0,
        'serving_size_g': 100
    },
    'печенье': {
        'calories': 417,
        'protein_g': 5.5,
        'fat_total_g': 13.0,
        'carbohydrates_total_g': 71.0,
        'serving_size_g': 100
    },
    'чипсы': {
        'calories': 536,
        'protein_g': 6.5,
        'fat_total_g': 37.0,
        'carbohydrates_total_g': 46.0,
        'serving_size_g': 100
    },
    'попкорн': {
        'calories': 375,
        'protein_g': 12.9,
        'fat_total_g': 5.0,
        'carbohydrates_total_g': 74.0,
        'serving_size_g': 100
    },
    'семечки': {
        'calories': 578,
        'protein_g': 20.7,
        'fat_total_g': 52.9,
        'carbohydrates_total_g': 4.0,
        'serving_size_g': 100
    },
    'кефир': {
        'calories': 59,
        'protein_g': 2.8,
        'fat_total_g': 3.2,
        'carbohydrates_total_g': 4.1,
        'serving_size_g': 100
    },
    'сметана': {
        'calories': 206,
        'protein_g': 2.8,
        'fat_total_g': 20.0,
        'carbohydrates_total_g': 3.2,
        'serving_size_g': 100
    },
    'масло': {
        'calories': 717,
        'protein_g': 0.8,
        'fat_total_g': 78.0,
        'carbohydrates_total_g': 1.3,
        'serving_size_g': 100
    },
    'майонез': {
        'calories': 621,
        'protein_g': 2.8,
        'fat_total_g': 67.0,
        'carbohydrates_total_g': 2.6,
        'serving_size_g': 100
    },
    'мед': {
        'calories': 329,
        'protein_g': 0.8,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 81.5,
        'serving_size_g': 100
    },
    'сахар': {
        'calories': 387,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 99.8,
        'serving_size_g': 100
    },
    'варенье': {
        'calories': 263,
        'protein_g': 0.4,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 68.0,
        'serving_size_g': 100
    },
    'джем': {
        'calories': 263,
        'protein_g': 0.4,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 68.0,
        'serving_size_g': 100
    },
    'конфеты': {
        'calories': 453,
        'protein_g': 2.2,
        'fat_total_g': 19.8,
        'carbohydrates_total_g': 69.3,
        'serving_size_g': 100
    },
    'вафли': {
        'calories': 539,
        'protein_g': 3.4,
        'fat_total_g': 30.2,
        'carbohydrates_total_g': 65.1,
        'serving_size_g': 100
    },
    'пряники': {
        'calories': 364,
        'protein_g': 4.8,
        'fat_total_g': 2.8,
        'carbohydrates_total_g': 77.7,
        'serving_size_g': 100
    },
    'крекеры': {
        'calories': 352,
        'protein_g': 9.0,
        'fat_total_g': 3.0,
        'carbohydrates_total_g': 71.0,
        'serving_size_g': 100
    },
    'булочка': {
        'calories': 339,
        'protein_g': 7.9,
        'fat_total_g': 9.4,
        'carbohydrates_total_g': 55.5,
        'serving_size_g': 100
    },
    'тост': {
        'calories': 313,
        'protein_g': 11.0,
        'fat_total_g': 4.0,
        'carbohydrates_total_g': 59.0,
        'serving_size_g': 100
    },
    'сэндвич': {
        'calories': 282,
        'protein_g': 12.0,
        'fat_total_g': 12.0,
        'carbohydrates_total_g': 30.0,
        'serving_size_g': 100
    },
    'роллы': {
        'calories': 176,
        'protein_g': 7.0,
        'fat_total_g': 7.0,
        'carbohydrates_total_g': 20.0,
        'serving_size_g': 100
    },
    'суши': {
        'calories': 176,
        'protein_g': 7.0,
        'fat_total_g': 7.0,
        'carbohydrates_total_g': 20.0,
        'serving_size_g': 100
    },
    'пирог': {
        'calories': 344,
        'protein_g': 4.4,
        'fat_total_g': 15.0,
        'carbohydrates_total_g': 51.0,
        'serving_size_g': 100
    },
    'запеканка': {
        'calories': 168,
        'protein_g': 17.6,
        'fat_total_g': 4.2,
        'carbohydrates_total_g': 14.2,
        'serving_size_g': 100
    },
    'сырники': {
        'calories': 220,
        'protein_g': 18.6,
        'fat_total_g': 7.0,
        'carbohydrates_total_g': 18.4,
        'serving_size_g': 100
    },
    'тефтели': {
        'calories': 217,
        'protein_g': 16.0,
        'fat_total_g': 10.0,
        'carbohydrates_total_g': 14.0,
        'serving_size_g': 100
    },
    'фрикадельки': {
        'calories': 217,
        'protein_g': 16.0,
        'fat_total_g': 10.0,
        'carbohydrates_total_g': 14.0,
        'serving_size_g': 100
    },
    'жаркое': {
        'calories': 142,
        'protein_g': 8.1,
        'fat_total_g': 6.3,
        'carbohydrates_total_g': 13.0,
        'serving_size_g': 100
    },
    'гуляш': {
        'calories': 156,
        'protein_g': 14.0,
        'fat_total_g': 9.2,
        'carbohydrates_total_g': 2.6,
        'serving_size_g': 100
    },
    'рагу': {
        'calories': 97,
        'protein_g': 5.5,
        'fat_total_g': 5.0,
        'carbohydrates_total_g': 8.0,
        'serving_size_g': 100
    },
    'яичница': {
        'calories': 196,
        'protein_g': 12.9,
        'fat_total_g': 15.0,
        'carbohydrates_total_g': 0.9,
        'serving_size_g': 100
    },
    'спагетти': {
        'calories': 371,
        'protein_g': 10.4,
        'fat_total_g': 1.1,
        'carbohydrates_total_g': 75.0,
        'serving_size_g': 100
    },
    'лапша': {
        'calories': 371,
        'protein_g': 10.4,
        'fat_total_g': 1.1,
        'carbohydrates_total_g': 75.0,
        'serving_size_g': 100
    },
    'ветчина': {
        'calories': 270,
        'protein_g': 22.6,
        'fat_total_g': 20.9,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'бекон': {
        'calories': 541,
        'protein_g': 23.0,
        'fat_total_g': 45.0,
        'carbohydrates_total_g': 1.4,
        'serving_size_g': 100
    },
    'креветки': {
        'calories': 106,
        'protein_g': 20.0,
        'fat_total_g': 1.7,
        'carbohydrates_total_g': 0.9,
        'serving_size_g': 100
    },
    'икра': {
        'calories': 263,
        'protein_g': 28.0,
        'fat_total_g': 17.9,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'соус': {
        'calories': 50,
        'protein_g': 1.0,
        'fat_total_g': 2.0,
        'carbohydrates_total_g': 8.0,
        'serving_size_g': 100
    },
    'кетчуп': {
        'calories': 112,
        'protein_g': 1.8,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 27.0,
        'serving_size_g': 100
    },
    'горчица': {
        'calories': 162,
        'protein_g': 10.0,
        'fat_total_g': 11.0,
        'carbohydrates_total_g': 5.0,
        'serving_size_g': 100
    },
    'уксус': {
        'calories': 11,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 3.0,
        'serving_size_g': 100
    },
    'специи': {
        'calories': 251,
        'protein_g': 12.0,
        'fat_total_g': 7.0,
        'carbohydrates_total_g': 43.0,
        'serving_size_g': 100
    },
    'приправы': {
        'calories': 251,
        'protein_g': 12.0,
        'fat_total_g': 7.0,
        'carbohydrates_total_g': 43.0,
        'serving_size_g': 100
    },
    'соль': {
        'calories': 0,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'мармелад': {
        'calories': 321,
        'protein_g': 0.0,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 79.4,
        'serving_size_g': 100
    },
    'голубцы': {
        'calories': 92,
        'protein_g': 6.7,
        'fat_total_g': 2.4,
        'carbohydrates_total_g': 10.9,
        'serving_size_g': 100
    },
    'манты': {
        'calories': 223,
        'protein_g': 13.3,
        'fat_total_g': 11.5,
        'carbohydrates_total_g': 16.0,
        'serving_size_g': 100
    },
    'хинкали': {
        'calories': 235,
        'protein_g': 11.0,
        'fat_total_g': 12.0,
        'carbohydrates_total_g': 22.0,
        'serving_size_g': 100
    },
    'лагман': {
        'calories': 86,
        'protein_g': 3.4,
        'fat_total_g': 2.4,
        'carbohydrates_total_g': 13.0,
        'serving_size_g': 100
    },
    'шашлык': {
        'calories': 324,
        'protein_g': 26.0,
        'fat_total_g': 23.0,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'винегрет': {
        'calories': 76,
        'protein_g': 1.6,
        'fat_total_g': 4.8,
        'carbohydrates_total_g': 6.7,
        'serving_size_g': 100
    },
    'оливье': {
        'calories': 198,
        'protein_g': 5.5,
        'fat_total_g': 16.5,
        'carbohydrates_total_g': 7.8,
        'serving_size_g': 100
    },
    'солянка': {
        'calories': 58,
        'protein_g': 3.4,
        'fat_total_g': 3.8,
        'carbohydrates_total_g': 2.1,
        'serving_size_g': 100
    },
    'харчо': {
        'calories': 75,
        'protein_g': 6.2,
        'fat_total_g': 2.2,
        'carbohydrates_total_g': 7.3,
        'serving_size_g': 100
    },
    'окрошка': {
        'calories': 60,
        'protein_g': 2.1,
        'fat_total_g': 3.1,
        'carbohydrates_total_g': 6.3,
        'serving_size_g': 100
    },
    'пшено': {
        'calories': 348,
        'protein_g': 11.5,
        'fat_total_g': 3.3,
        'carbohydrates_total_g': 69.3,
        'serving_size_g': 100
    },
    'манка': {
        'calories': 328,
        'protein_g': 10.3,
        'fat_total_g': 1.0,
        'carbohydrates_total_g': 70.6,
        'serving_size_g': 100
    },
    'перловка': {
        'calories': 320,
        'protein_g': 9.3,
        'fat_total_g': 1.1,
        'carbohydrates_total_g': 66.9,
        'serving_size_g': 100
    },
    'баранина': {
        'calories': 209,
        'protein_g': 24.0,
        'fat_total_g': 12.0,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'индейка': {
        'calories': 276,
        'protein_g': 19.5,
        'fat_total_g': 22.0,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'лосось': {
        'calories': 142,
        'protein_g': 19.8,
        'fat_total_g': 6.3,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'тунец': {
        'calories': 296,
        'protein_g': 29.9,
        'fat_total_g': 10.9,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'селедка': {
        'calories': 246,
        'protein_g': 17.7,
        'fat_total_g': 19.5,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'карп': {
        'calories': 112,
        'protein_g': 16.0,
        'fat_total_g': 5.3,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'крабы': {
        'calories': 96,
        'protein_g': 18.1,
        'fat_total_g': 1.9,
        'carbohydrates_total_g': 0.0,
        'serving_size_g': 100
    },
    'морковь': {
        'calories': 41,
        'protein_g': 0.9,
        'fat_total_g': 0.2,
        'carbohydrates_total_g': 9.6,
        'serving_size_g': 100
    },
    'капуста': {
        'calories': 25,
        'protein_g': 1.8,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 4.7,
        'serving_size_g': 100
    },
    'лук': {
        'calories': 40,
        'protein_g': 1.1,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 8.2,
        'serving_size_g': 100
    },
    'чеснок': {
        'calories': 149,
        'protein_g': 6.5,
        'fat_total_g': 0.5,
        'carbohydrates_total_g': 30.0,
        'serving_size_g': 100
    },
    'помидор': {
        'calories': 20,
        'protein_g': 0.6,
        'fat_total_g': 0.2,
        'carbohydrates_total_g': 4.2,
        'serving_size_g': 100
    },
    'огурец': {
        'calories': 15,
        'protein_g': 0.8,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 2.5,
        'serving_size_g': 100
    },
    'перец': {
        'calories': 27,
        'protein_g': 1.3,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 5.3,
        'serving_size_g': 100
    },
    'баклажан': {
        'calories': 24,
        'protein_g': 1.2,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 4.5,
        'serving_size_g': 100
    },
    'кабачок': {
        'calories': 24,
        'protein_g': 0.6,
        'fat_total_g': 0.3,
        'carbohydrates_total_g': 4.6,
        'serving_size_g': 100
    },
    'тыква': {
        'calories': 22,
        'protein_g': 1.0,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 4.4,
        'serving_size_g': 100
    },
    'свекла': {
        'calories': 40,
        'protein_g': 1.5,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 8.8,
        'serving_size_g': 100
    },
    'редис': {
        'calories': 19,
        'protein_g': 1.2,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 3.4,
        'serving_size_g': 100
    },
    'груша': {
        'calories': 57,
        'protein_g': 0.4,
        'fat_total_g': 0.3,
        'carbohydrates_total_g': 15.2,
        'serving_size_g': 100
    },
    'апельсин': {
        'calories': 36,
        'protein_g': 0.9,
        'fat_total_g': 0.2,
        'carbohydrates_total_g': 8.1,
        'serving_size_g': 100
    },
    'лимон': {
        'calories': 16,
        'protein_g': 0.9,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 3.0,
        'serving_size_g': 100
    },
    'виноград': {
        'calories': 65,
        'protein_g': 0.6,
        'fat_total_g': 0.2,
        'carbohydrates_total_g': 16.8,
        'serving_size_g': 100
    },
    'клубника': {
        'calories': 41,
        'protein_g': 0.8,
        'fat_total_g': 0.4,
        'carbohydrates_total_g': 7.7,
        'serving_size_g': 100
    },
    'малина': {
        'calories': 46,
        'protein_g': 0.8,
        'fat_total_g': 0.5,
        'carbohydrates_total_g': 8.3,
        'serving_size_g': 100
    },
    'черника': {
        'calories': 44,
        'protein_g': 1.1,
        'fat_total_g': 0.6,
        'carbohydrates_total_g': 7.6,
        'serving_size_g': 100
    },
    'вишня': {
        'calories': 52,
        'protein_g': 0.8,
        'fat_total_g': 0.2,
        'carbohydrates_total_g': 11.3,
        'serving_size_g': 100
    },
    'слива': {
        'calories': 42,
        'protein_g': 0.8,
        'fat_total_g': 0.3,
        'carbohydrates_total_g': 9.6,
        'serving_size_g': 100
    },
    'персик': {
        'calories': 46,
        'protein_g': 0.9,
        'fat_total_g': 0.3,
        'carbohydrates_total_g': 11.1,
        'serving_size_g': 100
    },
    'абрикос': {
        'calories': 44,
        'protein_g': 0.9,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 10.8,
        'serving_size_g': 100
    },
    'киви': {
        'calories': 47,
        'protein_g': 0.8,
        'fat_total_g': 0.4,
        'carbohydrates_total_g': 10.3,
        'serving_size_g': 100
    },
    'ананас': {
        'calories': 52,
        'protein_g': 0.4,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 13.4,
        'serving_size_g': 100
    },
    'манго': {
        'calories': 67,
        'protein_g': 0.5,
        'fat_total_g': 0.2,
        'carbohydrates_total_g': 17.0,
        'serving_size_g': 100
    },
    'авокадо': {
        'calories': 208,
        'protein_g': 2.0,
        'fat_total_g': 19.5,
        'carbohydrates_total_g': 6.0,
        'serving_size_g': 100
    },
    'гранат': {
        'calories': 72,
        'protein_g': 0.7,
        'fat_total_g': 0.6,
        'carbohydrates_total_g': 18.7,
        'serving_size_g': 100
    },
    'арбуз': {
        'calories': 25,
        'protein_g': 0.7,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 5.8,
        'serving_size_g': 100
    },
    'дыня': {
        'calories': 33,
        'protein_g': 0.6,
        'fat_total_g': 0.3,
        'carbohydrates_total_g': 7.4,
        'serving_size_g': 100
    },
    'хурма': {
        'calories': 67,
        'protein_g': 0.5,
        'fat_total_g': 0.4,
        'carbohydrates_total_g': 15.3,
        'serving_size_g': 100
    },
    'финики': {
        'calories': 274,
        'protein_g': 1.8,
        'fat_total_g': 0.1,
        'carbohydrates_total_g': 69.2,
        'serving_size_g': 100
    },
    'изюм': {
        'calories': 264,
        'protein_g': 2.9,
        'fat_total_g': 0.6,
        'carbohydrates_total_g': 66.0,
        'serving_size_g': 100
    },
    'курага': {
        'calories': 215,
        'protein_g': 5.2,
        'fat_total_g': 0.3,
        'carbohydrates_total_g': 51.0,
        'serving_size_g': 100
    },
    'чернослив': {
        'calories': 231,
        'protein_g': 2.2,
        'fat_total_g': 0.7,
        'carbohydrates_total_g': 57.5,
        'serving_size_g': 100
    },
    'грецкие орехи': {
        'calories': 654,
        'protein_g': 15.2,
        'fat_total_g': 65.2,
        'carbohydrates_total_g': 7.0,
        'serving_size_g': 100
    },
    'миндаль': {
        'calories': 645,
        'protein_g': 18.6,
        'fat_total_g': 57.7,
        'carbohydrates_total_g': 13.6,
        'serving_size_g': 100
    },
    'фундук': {
        'calories': 704,
        'protein_g': 16.1,
        'fat_total_g': 66.9,
        'carbohydrates_total_g': 9.4,
        'serving_size_g': 100
    },
    'кешью': {
        'calories': 600,
        'protein_g': 25.7,
        'fat_total_g': 54.1,
        'carbohydrates_total_g': 13.2,
        'serving_size_g': 100
    },
    'арахис': {
        'calories': 622,
        'protein_g': 26.3,
        'fat_total_g': 45.2,
        'carbohydrates_total_g': 9.9,
        'serving_size_g': 100
    },
    'фисташки': {
        'calories': 556,
        'protein_g': 20.0,
        'fat_total_g': 50.0,
        'carbohydrates_total_g': 7.0,
        'serving_size_g': 100
    },
    'кедровые орехи': {
        'calories': 673,
        'protein_g': 11.6,
        'fat_total_g': 61.0,
        'carbohydrates_total_g': 19.3,
        'serving_size_g': 100
    },
    'бразильский орех': {
        'calories': 659,
        'protein_g': 14.3,
        'fat_total_g': 67.1,
        'carbohydrates_total_g': 4.8,
        'serving_size_g': 100
    },
    'пекан': {
        'calories': 691,
        'protein_g': 9.2,
        'fat_total_g': 72.0,
        'carbohydrates_total_g': 4.3,
        'serving_size_g': 100
    },
    'макадамия': {
        'calories': 718,
        'protein_g': 7.9,
        'fat_total_g': 75.8,
        'carbohydrates_total_g': 5.2,
        'serving_size_g': 100
    },
    'энергетик': {
        'calories': 45,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 11.0,
        'serving_size_g': 100
    },
    'энергетический напиток': {
        'calories': 45,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 11.0,
        'serving_size_g': 100
    },
    'редбулл': {
        'calories': 45,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 11.0,
        'serving_size_g': 100
    },
    'red bull': {
        'calories': 45,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 11.0,
        'serving_size_g': 100
    },
    'вольт': {
        'calories': 48,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 12.0,
        'serving_size_g': 100
    },
    'volt': {
        'calories': 48,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 12.0,
        'serving_size_g': 100
    },
    'монстр': {
        'calories': 47,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 11.5,
        'serving_size_g': 100
    },
    'monster': {
        'calories': 47,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 11.5,
        'serving_size_g': 100
    },
    'адреналин раш': {
        'calories': 52,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 13.0,
        'serving_size_g': 100
    },
    'adrenaline rush': {
        'calories': 52,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 13.0,
        'serving_size_g': 100
    },
    'burn': {
        'calories': 49,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 12.2,
        'serving_size_g': 100
    },
    'flash': {
        'calories': 46,
        'protein_g': 0.0,
        'fat_total_g': 0.0,
        'carbohydrates_total_g': 11.5,
        'serving_size_g': 100
    },
}

def get_fallback_nutrition(food_name: str) -> Optional[Dict]:
    """
    Возвращает fallback данные о питательности
    """
    food_name_lower = food_name.lower().strip()
    
    # Прямое соответствие
    if food_name_lower in FALLBACK_NUTRITION:
        result = FALLBACK_NUTRITION[food_name_lower].copy()
        result['name'] = food_name
        return result
    
    # Частичное соответствие
    for key, nutrition in FALLBACK_NUTRITION.items():
        if key in food_name_lower or food_name_lower in key:
            result = nutrition.copy()
            result['name'] = food_name
            return result
    
    return None 