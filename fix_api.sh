#!/bin/bash

echo "🔧 Исправление API контейнера..."

echo "1️⃣ Проверка логов API..."
docker logs dieta-api-1 2>&1 | tail -20

echo "2️⃣ Остановка API контейнера..."
docker stop dieta-api-1 2>/dev/null
docker rm dieta-api-1 2>/dev/null

echo "3️⃣ Пересборка API контейнера..."
docker-compose -f docker-compose.minimal.yml build api

echo "4️⃣ Запуск API контейнера..."
docker-compose -f docker-compose.minimal.yml up -d api

echo "5️⃣ Ожидание запуска API..."
sleep 15

echo "6️⃣ Проверка статуса API..."
docker ps | grep api

echo "7️⃣ Проверка логов после запуска..."
docker logs dieta-api-1 2>&1 | tail -10

echo "8️⃣ Тестирование API..."
curl -I http://5.129.198.80/api/docs 2>/dev/null | head -1

echo "9️⃣ Исправление админа..."
API_CONTAINER=$(docker ps --format "{{.Names}}" | grep api | head -1)
if [ -n "$API_CONTAINER" ]; then
    echo "✅ Найден API контейнер: $API_CONTAINER"
    docker exec "$API_CONTAINER" python3 -c "
import asyncio
import bcrypt
from database.init_database import async_session_maker
from sqlalchemy import text

async def fix_admin():
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
                await session.execute(
                    text('UPDATE users SET password_hash = :password_hash, is_admin = true, is_verified = true WHERE email = :email'),
                    {'password_hash': hashed_password.decode('utf-8'), 'email': 'germannm@vk.com'}
                )
                print('✅ Админ исправлен')
            else:
                await session.execute(
                    text('INSERT INTO users (email, password_hash, is_admin, is_verified, created_at) VALUES (:email, :password_hash, true, true, NOW())'),
                    {'email': 'germannm@vk.com', 'password_hash': hashed_password.decode('utf-8')}
                )
                print('✅ Новый админ создан')
            
            await session.commit()
        except Exception as e:
            print(f'❌ Ошибка: {e}')
            await session.rollback()

asyncio.run(fix_admin())
"
else
    echo "❌ API контейнер не найден!"
fi

echo "✅ API исправлен!" 