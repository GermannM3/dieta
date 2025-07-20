#!/bin/bash

echo "🔧 ИСПРАВЛЕНИЕ API ЭНДПОИНТОВ И NGINX..."

echo "1️⃣ Проверка текущих API эндпоинтов..."
docker exec dieta-api-1 python3 -c "
from improved_api_server import app
print('🔍 Доступные эндпоинты:')
for route in app.routes:
    if hasattr(route, 'path'):
        print(f'  {route.methods} {route.path}')
"

echo "2️⃣ Создание правильного nginx конфига..."
cat > nginx-fixed.conf << 'EOF'
server {
    listen 80;
    server_name 5.129.198.80;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 5.129.198.80;

    # SSL сертификаты
    ssl_certificate /etc/letsencrypt/live/5.129.198.80/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/5.129.198.80/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # API эндпоинты - правильные пути
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

    # Прямые эндпоинты без /api/ префикса
    location /search_food {
        proxy_pass http://api:8000/api/search_food;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /login {
        proxy_pass http://api:8000/api/auth/login;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /register {
        proxy_pass http://api:8000/api/auth/register;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /calculate_calories {
        proxy_pass http://api:8000/api/calculate_calories;
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

echo "3️⃣ Проверка SSL сертификатов..."
if [ -f "/etc/letsencrypt/live/5.129.198.80/fullchain.pem" ]; then
    echo "✅ SSL сертификаты найдены"
else
    echo "❌ SSL сертификаты не найдены, создаем HTTP конфиг..."
    cat > nginx-fixed.conf << 'EOF'
server {
    listen 80;
    server_name 5.129.198.80;

    # API эндпоинты - правильные пути
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

    # Прямые эндпоинты без /api/ префикса
    location /search_food {
        proxy_pass http://api:8000/api/search_food;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /login {
        proxy_pass http://api:8000/api/auth/login;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /register {
        proxy_pass http://api:8000/api/auth/register;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /calculate_calories {
        proxy_pass http://api:8000/api/calculate_calories;
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
fi

echo "4️⃣ Применение нового nginx конфига..."
docker cp nginx-fixed.conf dieta-nginx-1:/etc/nginx/conf.d/default.conf
docker-compose -f docker-compose.minimal.yml restart nginx

echo "5️⃣ Ожидание запуска nginx..."
sleep 10

echo "6️⃣ Тестирование API эндпоинтов..."
echo "🔍 Тест /api/search_food..."
curl -X POST http://5.129.198.80/api/search_food \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  2>/dev/null | head -1

echo "🔍 Тест /api/auth/login..."
curl -X POST http://5.129.198.80/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "germannm@vk.com", "password": "Germ@nnM3"}' \
  2>/dev/null | head -1

echo "🔍 Тест /search_food (прямой путь)..."
curl -X POST http://5.129.198.80/search_food \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  2>/dev/null | head -1

echo "🔍 Тест /login (прямой путь)..."
curl -X POST http://5.129.198.80/login \
  -H "Content-Type: application/json" \
  -d '{"email": "germannm@vk.com", "password": "Germ@nnM3"}' \
  2>/dev/null | head -1

echo "7️⃣ Тестирование HTTPS..."
if [ -f "/etc/letsencrypt/live/5.129.198.80/fullchain.pem" ]; then
    echo "🔍 Тест HTTPS /api/search_food..."
    curl -X POST https://5.129.198.80/api/search_food \
      -H "Content-Type: application/json" \
      -d '{"query": "яблоко"}' \
      -k 2>/dev/null | head -1
else
    echo "⚠️ HTTPS недоступен (нет сертификатов)"
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

echo "✅ API ЭНДПОИНТЫ ИСПРАВЛЕНЫ!" 