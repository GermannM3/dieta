#!/bin/bash

echo "🔍 ДИАГНОСТИКА ПРОБЛЕМ API И БД..."

echo "1️⃣ ПРОВЕРКА ЛОГОВ API..."
docker-compose logs api | tail -20

echo ""
echo "2️⃣ ПРОВЕРКА ПОДКЛЮЧЕНИЯ К БД ВНУТРИ API КОНТЕЙНЕРА..."
docker exec dieta-api-1 python3 -c "
import asyncio
from database.init_database import async_session_maker
from sqlalchemy import text

async def test_db():
    print('🔍 Тестирование подключения к Neon БД...')
    
    async with async_session_maker() as session:
        try:
            # Тест простого запроса
            result = await session.execute(text('SELECT 1 as test'))
            row = result.fetchone()
            print(f'✅ БД подключение: {row.test}')
            
            # Тест таблицы users
            result = await session.execute(text('SELECT COUNT(*) as count FROM users'))
            row = result.fetchone()
            print(f'✅ Пользователей в БД: {row.count}')
            
            # Тест таблицы meals
            result = await session.execute(text('SELECT COUNT(*) as count FROM meals'))
            row = result.fetchone()
            print(f'✅ Приемов пищи в БД: {row.count}')
            
        except Exception as e:
            print(f'❌ Ошибка БД: {e}')

asyncio.run(test_db())
"

echo ""
echo "3️⃣ ПРОВЕРКА GIGACHAT API..."
docker exec dieta-api-1 python3 -c "
import asyncio
from api.ai_api.gigachat_api import gigachat

async def test_gigachat():
    print('🔍 Тестирование GigaChat API...')
    
    try:
        # Тест получения токена
        print('🔑 Получение токена доступа...')
        token = await gigachat.get_access_token()
        if token:
            print(f'✅ Токен получен: {token[:20]}...')
        else:
            print('❌ Не удалось получить токен')
            return
        
        # Тест простого запроса
        print('💬 Тест простого запроса...')
        response = await gigachat.simple_completion('Привет! Как дела?')
        if response:
            print(f'✅ Ответ получен: {response[:100]}...')
        else:
            print('❌ Нет ответа от GigaChat')
            
    except Exception as e:
        print(f'❌ Ошибка GigaChat: {e}')

asyncio.run(test_gigachat())
"

echo ""
echo "4️⃣ ПРОВЕРКА NUTRITION API..."
docker exec dieta-api-1 python3 -c "
import asyncio
from api.ai_api.nutrition_api import NutritionAPI

async def test_nutrition():
    print('🔍 Тестирование Nutrition API...')
    
    try:
        nutrition = NutritionAPI()
        
        # Тест подсчета калорий
        print('🍎 Тест подсчета калорий для яблока...')
        result = await nutrition.get_nutrition_data('яблоко', 100)
        print(f'✅ Результат: {result}')
        
        # Тест fallback данных
        print('🍕 Тест fallback данных для пиццы...')
        result = await nutrition.get_fallback_nutrition('пицца', 200)
        print(f'✅ Fallback результат: {result}')
        
    except Exception as e:
        print(f'❌ Ошибка Nutrition API: {e}')

asyncio.run(test_nutrition())
"

echo ""
echo "5️⃣ ПРОВЕРКА АВТОРИЗАЦИИ АДМИНА..."
docker exec dieta-api-1 python3 -c "
import asyncio
import bcrypt
from database.init_database import async_session_maker
from sqlalchemy import text

async def test_admin():
    print('🔍 Тестирование авторизации админа...')
    
    async with async_session_maker() as session:
        try:
            # Проверяем админа
            result = await session.execute(
                text('SELECT id, email, is_admin, is_verified FROM users WHERE email = :email'),
                {'email': 'germannm@vk.com'}
            )
            user = result.fetchone()
            
            if user:
                print(f'✅ Пользователь найден: {user.email}')
                print(f'   ID: {user.id}')
                print(f'   Админ: {user.is_admin}')
                print(f'   Подтвержден: {user.is_verified}')
                
                # Тест пароля
                test_password = 'Germ@nnM3'
                result = await session.execute(
                    text('SELECT password_hash FROM users WHERE email = :email'),
                    {'email': 'germannm@vk.com'}
                )
                password_row = result.fetchone()
                
                if password_row and password_row.password_hash:
                    if bcrypt.checkpw(test_password.encode('utf-8'), password_row.password_hash.encode('utf-8')):
                        print('✅ Пароль корректный')
                    else:
                        print('❌ Пароль неверный')
                else:
                    print('❌ Хеш пароля не найден')
            else:
                print('❌ Пользователь не найден')
                
        except Exception as e:
            print(f'❌ Ошибка проверки админа: {e}')

asyncio.run(test_admin())
"

echo ""
echo "6️⃣ ПРОВЕРКА API ЭНДПОИНТОВ..."
echo "🔍 Тест /api/search_food..."
curl -X POST http://5.129.198.80/api/search_food \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  2>/dev/null | head -1

echo ""
echo "🔍 Тест /api/auth/login..."
curl -X POST http://5.129.198.80/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "germannm@vk.com", "password": "Germ@nnM3"}' \
  2>/dev/null | head -1

echo ""
echo "7️⃣ ФИНАЛЬНАЯ ПРОВЕРКА..."
docker ps

echo ""
echo "✅ ДИАГНОСТИКА ЗАВЕРШЕНА!" 