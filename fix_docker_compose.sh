#!/bin/bash

echo "🔧 ИСПРАВЛЕНИЕ DOCKER COMPOSE И ВСЕХ ПРОБЛЕМ!"

echo "1️⃣ ОСТАНОВКА ВСЕГО..."
docker-compose -f docker-compose.minimal.yml down

echo "2️⃣ СОЗДАНИЕ ПРАВИЛЬНОГО NGINX КОНФИГА..."
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
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Fallback HTTP сервер для IP
server {
    listen 80;
    server_name 5.129.198.80;

    # API эндпоинты
    location /api/ {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo "3️⃣ ОБНОВЛЕНИЕ DOCKER COMPOSE..."
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

echo "4️⃣ ИСПРАВЛЕНИЕ ПАРОЛЯ АДМИНА В БД..."
docker-compose -f docker-compose.minimal.yml up -d api
sleep 10

echo "5️⃣ ТЕСТИРОВАНИЕ API ВНУТРИ КОНТЕЙНЕРА..."
docker exec dieta-api-1 python3 -c "
import asyncio
import bcrypt
from database.init_database import async_session_maker
from database.crud import get_user_by_tg_id, create_user, update_user
from sqlalchemy import text

async def fix_admin():
    print('🔧 Исправление админа...')
    
    async with async_session_maker() as session:
        try:
            # Проверяем существующего админа
            admin = await get_user_by_tg_id(session, 389694638)
            
            if admin:
                print('✅ Админ найден, обновляем пароль...')
                # Создаем новый хеш пароля
                password = 'admin123'
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
                
                # Обновляем пароль
                admin.password_hash = hashed.decode('utf-8')
                admin.is_admin = True
                await session.commit()
                print('✅ Пароль админа обновлен')
            else:
                print('❌ Админ не найден, создаем нового...')
                # Создаем нового админа
                password = 'admin123'
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
                
                new_admin = {
                    'tg_id': 389694638,
                    'name': 'Admin',
                    'password_hash': hashed.decode('utf-8'),
                    'is_admin': True
                }
                
                await create_user(session, new_admin)
                print('✅ Новый админ создан')
                
        except Exception as e:
            print(f'❌ Ошибка: {e}')

asyncio.run(fix_admin())
"

echo "6️⃣ ЗАПУСК ВСЕХ СЕРВИСОВ..."
docker-compose -f docker-compose.minimal.yml up -d

echo "7️⃣ ПРОВЕРКА СТАТУСА..."
sleep 10
docker-compose -f docker-compose.minimal.yml ps

echo "8️⃣ ТЕСТИРОВАНИЕ API..."
curl -X POST http://localhost/api/search_food \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  -w "\nHTTP Status: %{http_code}\n"

echo "9️⃣ ТЕСТИРОВАНИЕ FRONTEND..."
curl -I http://localhost/ | head -5

echo "🔟 ТЕСТИРОВАНИЕ HTTPS..."
curl -I https://tvoi-kalkulyator.ru/ | head -5

echo "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo "🔑 Логин админа: admin123"
echo "🌐 Сайт: https://tvoi-kalkulyator.ru"
echo "🤖 Бот: @tvoy_diet_bot" 