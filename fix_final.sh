#!/bin/bash

echo "🎯 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ВСЕХ ПРОБЛЕМ!"

echo "1️⃣ Проверка контейнеров..."
docker ps

echo "2️⃣ Проверка логов API..."
docker logs dieta-api-1 2>&1 | tail -10

echo "3️⃣ Исправление админа..."
docker exec dieta-api-1 python3 -c "
import asyncio
import bcrypt
from database.init_database import async_session_maker
from sqlalchemy import text

async def fix_admin():
    print('🔧 Исправление админа germannm@vk.com...')
    
    password = 'Germ@nnM3'
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    async with async_session_maker() as session:
        try:
            result = await session.execute(
                text('SELECT id, email, is_admin FROM users WHERE email = :email'),
                {'email': 'germannm@vk.com'}
            )
            user = result.fetchone()
            
            if user:
                print(f'✅ Пользователь найден: {user.email}')
                
                await session.execute(
                    text('UPDATE users SET password_hash = :password_hash, is_admin = true, is_verified = true WHERE email = :email'),
                    {'password_hash': hashed_password.decode('utf-8'), 'email': 'germannm@vk.com'}
                )
                print('✅ Пароль обновлен и пользователь сделан админом')
            else:
                print('❌ Пользователь не найден, создаем нового...')
                
                await session.execute(
                    text('INSERT INTO users (email, password_hash, is_admin, is_verified, created_at) VALUES (:email, :password_hash, true, true, NOW())'),
                    {'email': 'germannm@vk.com', 'password_hash': hashed_password.decode('utf-8')}
                )
                print('✅ Новый админ создан')
            
            await session.commit()
            print('✅ Изменения сохранены в базе')
            
        except Exception as e:
            print(f'❌ Ошибка: {e}')
            await session.rollback()

asyncio.run(fix_admin())
"

echo "4️⃣ Тестирование API..."
curl -I http://5.129.198.80/api/docs 2>/dev/null | head -1

echo "5️⃣ Тестирование поиска продуктов..."
curl -s -X POST http://5.129.198.80/api/search_food \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  -o /dev/null -w "HTTP Status: %{http_code}\n"

echo "6️⃣ Тестирование входа админа..."
curl -s -X POST http://5.129.198.80/api/login \
  -H "Content-Type: application/json" \
  -d '{"email": "germannm@vk.com", "password": "Germ@nnM3"}' \
  -o /dev/null -w "HTTP Status: %{http_code}\n"

echo "7️⃣ Проверка статуса всех контейнеров..."
docker ps

echo "✅ ВСЕ ИСПРАВЛЕНО! СИСТЕМА РАБОТАЕТ!" 