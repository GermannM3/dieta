#!/bin/bash

echo "🔧 ИСПРАВЛЕНИЕ HTTPS И ПРОВЕРКА СВЯЗЕЙ..."

echo "1️⃣ Проверка SSL сертификатов..."
if [ -d "/etc/letsencrypt/live/5.129.198.80" ]; then
    echo "✅ SSL сертификаты найдены:"
    ls -la /etc/letsencrypt/live/5.129.198.80/
else
    echo "❌ SSL сертификаты не найдены в /etc/letsencrypt/live/5.129.198.80/"
fi

echo "2️⃣ Проверка других возможных путей сертификатов..."
find /etc -name "*.pem" -path "*5.129.198.80*" 2>/dev/null
find /opt -name "*.pem" -path "*ssl*" 2>/dev/null

echo "3️⃣ Проверка текущего nginx конфига..."
docker exec dieta-nginx-1 cat /etc/nginx/conf.d/default.conf

echo "4️⃣ Создание правильного nginx конфига с SSL..."
cat > nginx-ssl-working.conf << 'EOF'
server {
    listen 80;
    server_name 5.129.198.80;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 5.129.198.80;

    # Попробуем разные пути к сертификатам
    ssl_certificate /etc/letsencrypt/live/5.129.198.80/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/5.129.198.80/privkey.pem;

    # Fallback если основной путь не работает
    ssl_certificate /opt/dieta/ssl/fullchain.pem;
    ssl_certificate_key /opt/dieta/ssl/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # API endpoints - исправляем пути
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

    # API без /api/ префикса
    location /search_food {
        proxy_pass http://api:8000/search_food;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /login {
        proxy_pass http://api:8000/login;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /register {
        proxy_pass http://api:8000/register;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /calculate_calories {
        proxy_pass http://api:8000/calculate_calories;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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

echo "5️⃣ Проверка подключения к Neon БД..."
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

echo "6️⃣ Проверка API эндпоинтов..."
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
            
            # Тест /search_food
            data = {'query': 'яблоко'}
            async with session.post('http://localhost:8000/search_food', json=data) as resp:
                print(f'✅ /search_food: {resp.status}')
                if resp.status == 200:
                    result = await resp.json()
                    print(f'   Результат: {len(result)} продуктов найдено')
            
            # Тест /login
            data = {'email': 'germannm@vk.com', 'password': 'Germ@nnM3'}
            async with session.post('http://localhost:8000/login', json=data) as resp:
                print(f'✅ /login: {resp.status}')
                if resp.status == 200:
                    result = await resp.json()
                    print(f'   Результат: {result.get(\"message\", \"OK\")}')
            
        except Exception as e:
            print(f'❌ Ошибка тестирования API: {e}')

asyncio.run(test_api())
"

echo "7️⃣ Проверка frontend..."
docker exec dieta-frontend-1 curl -I http://localhost:3000 2>/dev/null | head -1

echo "8️⃣ Перезапуск nginx с новым конфигом..."
docker cp nginx-ssl-working.conf dieta-nginx-1:/etc/nginx/conf.d/default.conf
docker-compose -f docker-compose.minimal.yml restart nginx

echo "9️⃣ Ожидание запуска..."
sleep 10

echo "🔟 Тестирование HTTPS..."
curl -I https://5.129.198.80/api/docs 2>/dev/null | head -1
curl -I https://5.129.198.80/ 2>/dev/null | head -1

echo "1️⃣1️⃣ Тестирование API через nginx..."
curl -X POST https://5.129.198.80/search_food \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  2>/dev/null | head -1

echo "1️⃣2️⃣ Финальная проверка..."
docker ps

echo "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!" 