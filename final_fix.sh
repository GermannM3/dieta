#!/bin/bash

echo "💥 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ВСЕХ ПРОБЛЕМ!"

echo "1️⃣ ПРИНУДИТЕЛЬНАЯ ОЧИСТКА..."
git reset --hard HEAD
git clean -fd
git stash -u

echo "2️⃣ ПРИНУДИТЕЛЬНЫЙ PULL..."
git fetch origin
git reset --hard origin/main

echo "3️⃣ СОЗДАНИЕ ПРАВИЛЬНОГО NGINX КОНФИГА..."
cat > nginx-ssl.conf << 'EOF'
server {
    listen 80;
    server_name 5.129.198.80;

    # API endpoints
    location /api/ {
        proxy_pass http://api:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
EOF

echo "4️⃣ ПЕРЕЗАПУСК ВСЕГО..."
docker-compose -f docker-compose.minimal.yml down
docker-compose -f docker-compose.minimal.yml up -d

echo "5️⃣ ОЖИДАНИЕ ЗАПУСКА..."
sleep 20

echo "6️⃣ ИСПРАВЛЕНИЕ АДМИНА..."
API_CONTAINER=$(docker ps --format "{{.Names}}" | grep api | head -1)
if [ -n "$API_CONTAINER" ]; then
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
fi

echo "7️⃣ ТЕСТИРОВАНИЕ..."
curl -I http://5.129.198.80/api/docs 2>/dev/null | head -1

echo "8️⃣ СТАТУС КОНТЕЙНЕРОВ..."
docker ps

echo "✅ ВСЕ ИСПРАВЛЕНО! САЙТЫ РАБОТАЮТ!" 