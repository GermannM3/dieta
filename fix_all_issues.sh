#!/bin/bash

echo "🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ВСЕХ ПРОБЛЕМ!"

echo "1️⃣ ОСТАНОВКА ВСЕГО..."
docker-compose -f docker-compose.minimal.yml down
docker-compose -f docker-compose.production.yml down

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
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
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
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

echo "3️⃣ ИСПРАВЛЕНИЕ ПАРОЛЯ АДМИНА В БД..."
docker-compose -f docker-compose.production.yml up -d api
sleep 15

echo "4️⃣ СОЗДАНИЕ/ОБНОВЛЕНИЕ АДМИНА..."
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
                password = 'Germ@nnM3'
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
                
                # Обновляем пароль и email
                admin.password_hash = hashed.decode('utf-8')
                admin.email = 'germannm@vk.com'
                admin.is_admin = True
                await session.commit()
                print('✅ Пароль админа обновлен: Germ@nnM3')
                print('✅ Email админа: germannm@vk.com')
            else:
                print('❌ Админ не найден, создаем нового...')
                # Создаем нового админа
                password = 'Germ@nnM3'
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
                
                new_admin = {
                    'tg_id': 389694638,
                    'name': 'Admin',
                    'email': 'germannm@vk.com',
                    'password_hash': hashed.decode('utf-8'),
                    'is_admin': True
                }
                
                await create_user(session, new_admin)
                print('✅ Новый админ создан: Germ@nnM3')
                print('✅ Email админа: germannm@vk.com')
                
        except Exception as e:
            print(f'❌ Ошибка: {e}')

asyncio.run(fix_admin())
"

echo "5️⃣ ЗАПУСК ВСЕХ СЕРВИСОВ..."
docker-compose -f docker-compose.production.yml up -d

echo "6️⃣ ПРОВЕРКА СТАТУСА..."
sleep 10
docker-compose -f docker-compose.production.yml ps

echo "7️⃣ ТЕСТИРОВАНИЕ API ВНУТРИ КОНТЕЙНЕРА..."
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
                    print(f'📊 Результат: {json.dumps(result, ensure_ascii=False)}')
            
            # Тест /api/auth/login
            login_data = {
                'email': 'germannm@vk.com',
                'password': 'Germ@nnM3'
            }
            async with session.post('http://localhost:8000/api/auth/login', json=login_data) as resp:
                print(f'✅ /api/auth/login: {resp.status}')
                if resp.status == 200:
                    result = await resp.json()
                    print(f'🔑 Авторизация: {json.dumps(result, ensure_ascii=False)}')
                else:
                    text = await resp.text()
                    print(f'❌ Ошибка авторизации: {text}')
                    
        except Exception as e:
            print(f'❌ Ошибка тестирования: {e}')

asyncio.run(test_api())
"

echo "8️⃣ ТЕСТИРОВАНИЕ FRONTEND..."
curl -I http://localhost/ | head -5

echo "9️⃣ ТЕСТИРОВАНИЕ HTTPS..."
curl -I https://tvoi-kalkulyator.ru/ | head -5

echo "🔟 ПРОВЕРКА ЛОГОВ..."
echo "📋 Логи API:"
docker-compose -f docker-compose.production.yml logs api --tail=10

echo "📋 Логи бота:"
docker-compose -f docker-compose.production.yml logs bot --tail=5

echo "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo "🔑 Логин админа: germannm@vk.com"
echo "🔑 Пароль админа: Germ@nnM3"
echo "🌐 Сайт: https://tvoi-kalkulyator.ru"
echo "🤖 Бот: @tvoy_diet_bot"
echo "📧 MailHog UI: http://5.129.198.80:8025" 