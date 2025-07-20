#!/bin/bash

echo "💥 РАДИКАЛЬНОЕ ИСПРАВЛЕНИЕ ВСЕХ ПРОБЛЕМ!"

echo "1️⃣ ОСТАНОВКА ВСЕГО..."
docker-compose -f docker-compose.minimal.yml down

echo "2️⃣ ОЧИСТКА СТАРЫХ КОНФИГОВ..."
rm -f nginx-ssl.conf nginx-final.conf

echo "3️⃣ СОЗДАНИЕ ПРАВИЛЬНОГО NGINX КОНФИГА..."
cat > nginx-correct.conf << 'EOF'
# Основной сервер для доменов с SSL
server {
    listen 80;
    server_name tvoi-kalkulyator.ru www.tvoi-kalkulyator.ru;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tvoi-kalkulyator.ru www.tvoi-kalkulyator.ru;

    ssl_certificate /etc/letsencrypt/live/tvoi-kalkulyator.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tvoi-kalkulyator.ru/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # API эндпоинты
    location /api/ {
        proxy_pass http://api:8000/api/;
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

# HTTP сервер для IP (fallback)
server {
    listen 80;
    server_name 5.129.198.80;

    # API эндпоинты
    location /api/ {
        proxy_pass http://api:8000/api/;
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

echo "4️⃣ ОБНОВЛЕНИЕ DOCKER COMPOSE..."
cat > docker-compose.minimal.yml << 'EOF'
version: '3.8'

services:
  # FastAPI Backend
  api:
    build:
      context: .
      dockerfile: Dockerfile
    command: python improved_api_server.py
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network

  # Telegram Bot
  bot:
    build:
      context: .
      dockerfile: Dockerfile.bot
    env_file:
      - .env
    environment:
      - API_BASE_URL=http://api:8000
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network

  # React Frontend
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    restart: unless-stopped
    depends_on:
      - api
    networks:
      - app-network

  # Nginx Reverse Proxy (исправленный)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-correct.conf:/etc/nginx/conf.d/default.conf
      - /etc/letsencrypt/live:/etc/letsencrypt/live:ro
      - /etc/letsencrypt/archive:/etc/letsencrypt/archive:ro
    restart: unless-stopped
    depends_on:
      - frontend
      - api
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
EOF

echo "5️⃣ ЗАПУСК ВСЕГО ЗАНОВО..."
docker-compose -f docker-compose.minimal.yml up -d

echo "6️⃣ ОЖИДАНИЕ ЗАПУСКА..."
sleep 30

echo "7️⃣ ПРОВЕРКА КОНТЕЙНЕРОВ..."
docker ps

echo "8️⃣ ПРОВЕРКА API ВНУТРИ КОНТЕЙНЕРА..."
docker exec dieta-api-1 python3 -c "
import asyncio
import aiohttp
import json

async def test_api():
    print('🔍 Тестирование API эндпоинтов внутри контейнера...')
    
    async with aiohttp.ClientSession() as session:
        try:
            # Тест /docs
            async with session.get('http://localhost:8000/docs') as resp:
                print(f'✅ /docs: {resp.status}')
            
            # Тест /api/search_food
            data = {'query': 'яблоко'}
            async with session.post('http://localhost:8000/api/search_food', json=data) as resp:
                print(f'✅ /api/search_food: {resp.status}')
                if resp.status == 200:
                    result = await resp.json()
                    print(f'   Результат: {len(result.get(\"foods\", []))} продуктов найдено')
            
            # Тест /api/auth/login
            data = {'email': 'germannm@vk.com', 'password': 'Germ@nnM3'}
            async with session.post('http://localhost:8000/api/auth/login', json=data) as resp:
                print(f'✅ /api/auth/login: {resp.status}')
                if resp.status == 200:
                    result = await resp.json()
                    print(f'   Результат: {result.get(\"message\", \"OK\")}')
            
        except Exception as e:
            print(f'❌ Ошибка тестирования API: {e}')

asyncio.run(test_api())
"

echo "9️⃣ ПРОВЕРКА FRONTEND..."
docker exec dieta-frontend-1 curl -I http://localhost:3000 2>/dev/null | head -1

echo "🔟 ПРОВЕРКА NGINX КОНФИГА..."
docker exec dieta-nginx-1 nginx -t

echo "1️⃣1️⃣ ТЕСТИРОВАНИЕ СВЯЗЕЙ..."
echo "🔍 Тест HTTP API по IP..."
curl -X POST http://5.129.198.80/api/search_food \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  2>/dev/null | head -1

echo "🔍 Тест HTTP Frontend по IP..."
curl -I http://5.129.198.80/ 2>/dev/null | head -1

echo "🔍 Тест HTTPS API по домену..."
curl -X POST https://tvoi-kalkulyator.ru/api/search_food \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  -k 2>/dev/null | head -1

echo "🔍 Тест HTTPS Frontend по домену..."
curl -I https://tvoi-kalkulyator.ru/ -k 2>/dev/null | head -1

echo "1️⃣2️⃣ ИСПРАВЛЕНИЕ АДМИНА..."
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

echo "1️⃣3️⃣ ФИНАЛЬНАЯ ПРОВЕРКА..."
docker ps

echo "✅ РАДИКАЛЬНОЕ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo ""
echo "🌐 Сайты должны быть доступны:"
echo "   HTTP:  http://5.129.198.80"
echo "   HTTPS: https://tvoi-kalkulyator.ru"
echo ""
echo "🔧 API эндпоинты:"
echo "   http://5.129.198.80/api/search_food"
echo "   http://5.129.198.80/api/auth/login"
echo ""
echo "👤 Админ: germannm@vk.com / Germ@nnM3" 