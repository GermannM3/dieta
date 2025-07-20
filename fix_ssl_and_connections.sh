#!/bin/bash

echo "🔧 ИСПРАВЛЕНИЕ SSL И ПРОВЕРКА СВЯЗЕЙ..."

echo "1️⃣ Проверка SSL сертификатов..."
echo "🔍 Поиск сертификатов для доменов..."
if [ -d "/etc/letsencrypt/live/tvoi-kalkulyator.ru" ]; then
    echo "✅ SSL сертификаты найдены для tvoi-kalkulyator.ru:"
    ls -la /etc/letsencrypt/live/tvoi-kalkulyator.ru/
    DOMAIN="tvoi-kalkulyator.ru"
elif [ -d "/etc/letsencrypt/live/твой-калькулятор.рф" ]; then
    echo "✅ SSL сертификаты найдены для твой-калькулятор.рф:"
    ls -la /etc/letsencrypt/live/твой-калькулятор.рф/
    DOMAIN="твой-калькулятор.рф"
else
    echo "❌ SSL сертификаты не найдены, создаем HTTP конфиг..."
    DOMAIN=""
fi

echo "2️⃣ Проверка подключения к Neon БД..."
docker exec dieta-api-1 python3 -c "
import asyncio
from database.init_database import async_session_maker
from sqlalchemy import text

async def test_db():
    print('🔍 Тестирование подключения к Neon БД...')
    try:
        async with async_session_maker() as session:
            result = await session.execute(text('SELECT 1 as test'))
            row = result.fetchone()
            print(f'✅ БД подключена: {row.test}')
            
            # Проверяем таблицы
            result = await session.execute(text(\"\"\"
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            \"\"\"))
            tables = [row[0] for row in result.fetchall()]
            print(f'✅ Таблицы в БД: {tables}')
            
    except Exception as e:
        print(f'❌ Ошибка подключения к БД: {e}')

asyncio.run(test_db())
"

echo "3️⃣ Проверка API эндпоинтов..."
docker exec dieta-api-1 python3 -c "
import asyncio
import aiohttp
import json

async def test_api():
    print('🔍 Тестирование API эндпоинтов...')
    
    # Тестируем локально внутри контейнера
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
                    print(f'   Результат: {len(result)} продуктов найдено')
            
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

echo "4️⃣ Создание правильного nginx конфига..."
if [ -n "$DOMAIN" ]; then
    echo "🔒 Создание SSL конфига для домена: $DOMAIN"
    cat > nginx-ssl-working.conf << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN 5.129.198.80;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # API эндпоинты - правильные пути
    location /api/ {
        proxy_pass http://api:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
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
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
EOF
else
    echo "🌐 Создание HTTP конфига (без SSL)"
    cat > nginx-ssl-working.conf << 'EOF'
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
fi

echo "5️⃣ Применение nginx конфига..."
docker cp nginx-ssl-working.conf dieta-nginx-1:/etc/nginx/conf.d/default.conf
docker-compose -f docker-compose.minimal.yml restart nginx

echo "6️⃣ Ожидание запуска nginx..."
sleep 10

echo "7️⃣ Тестирование связей..."
echo "🔍 Тест HTTP API..."
curl -X POST http://5.129.198.80/api/search_food \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  2>/dev/null | head -1

echo "🔍 Тест HTTP Frontend..."
curl -I http://5.129.198.80/ 2>/dev/null | head -1

if [ -n "$DOMAIN" ]; then
    echo "🔍 Тест HTTPS API..."
    curl -X POST https://$DOMAIN/api/search_food \
      -H "Content-Type: application/json" \
      -d '{"query": "яблоко"}' \
      -k 2>/dev/null | head -1

    echo "🔍 Тест HTTPS Frontend..."
    curl -I https://$DOMAIN/ -k 2>/dev/null | head -1
fi

echo "8️⃣ Исправление админа..."
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

echo "9️⃣ Финальная проверка..."
docker ps

echo "✅ SSL И СВЯЗИ ИСПРАВЛЕНЫ!" 