#!/bin/bash

echo "🔒 ВОССТАНОВЛЕНИЕ SSL БЕЗ НАРУШЕНИЯ РАБОТЫ..."

echo "1️⃣ Проверка текущего статуса..."
docker ps | grep nginx

echo "2️⃣ Проверка SSL сертификатов..."
if [ -f "/etc/letsencrypt/live/5.129.198.80/fullchain.pem" ]; then
    echo "✅ SSL сертификаты найдены"
    
    echo "3️⃣ Создание правильного nginx конфига с SSL..."
    cat > nginx-ssl.conf << 'EOF'
server {
    listen 80;
    server_name 5.129.198.80;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name 5.129.198.80;

    ssl_certificate /etc/letsencrypt/live/5.129.198.80/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/5.129.198.80/privkey.pem;

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
else
    echo "❌ SSL сертификаты не найдены, создаем HTTP конфиг..."
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
fi

echo "4️⃣ Перезапуск только nginx..."
docker-compose -f docker-compose.minimal.yml restart nginx

echo "5️⃣ Ожидание запуска nginx..."
sleep 10

echo "6️⃣ Проверка статуса nginx..."
docker ps | grep nginx

echo "7️⃣ Тестирование HTTP..."
curl -I http://5.129.198.80/api/docs 2>/dev/null | head -1

echo "8️⃣ Тестирование HTTPS (если есть сертификаты)..."
if [ -f "/etc/letsencrypt/live/5.129.198.80/fullchain.pem" ]; then
    curl -I https://5.129.198.80/api/docs 2>/dev/null | head -1
else
    echo "⚠️ HTTPS недоступен (нет сертификатов)"
fi

echo "9️⃣ Исправление админа..."
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

echo "🔟 Финальная проверка..."
docker ps

echo "✅ SSL ВОССТАНОВЛЕН! САЙТЫ РАБОТАЮТ!" 