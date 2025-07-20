#!/bin/bash

echo "🔒 Исправление SSL и nginx..."

echo "1️⃣ Проверка SSL сертификатов..."
if [ ! -f "/etc/letsencrypt/live/5.129.198.80/fullchain.pem" ]; then
    echo "❌ SSL сертификаты не найдены!"
    echo "🔧 Создание временного nginx конфига без SSL..."
    
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
    }

    # Frontend
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
else
    echo "✅ SSL сертификаты найдены!"
fi

echo "2️⃣ Остановка nginx..."
docker stop dieta-nginx-1 2>/dev/null

echo "3️⃣ Запуск nginx..."
docker-compose -f docker-compose.minimal.yml up -d nginx

echo "4️⃣ Ожидание запуска..."
sleep 10

echo "5️⃣ Проверка статуса nginx..."
docker ps | grep nginx

echo "6️⃣ Тестирование HTTP..."
curl -I http://5.129.198.80/api/docs 2>/dev/null | head -1

echo "7️⃣ Исправление админа..."
API_CONTAINER=$(docker ps --format "{{.Names}}" | grep api | head -1)
if [ -n "$API_CONTAINER" ]; then
    echo "✅ Найден API контейнер: $API_CONTAINER"
    docker exec "$API_CONTAINER" python3 -c "
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
                    text('''
                        UPDATE users 
                        SET password_hash = :password_hash, 
                            is_admin = true,
                            is_verified = true
                        WHERE email = :email
                    '''),
                    {
                        'password_hash': hashed_password.decode('utf-8'),
                        'email': 'germannm@vk.com'
                    }
                )
                print('✅ Пароль обновлен и пользователь сделан админом')
            else:
                print('❌ Пользователь не найден, создаем нового...')
                
                await session.execute(
                    text('''
                        INSERT INTO users (email, password_hash, is_admin, is_verified, created_at)
                        VALUES (:email, :password_hash, true, true, NOW())
                    '''),
                    {
                        'email': 'germannm@vk.com',
                        'password_hash': hashed_password.decode('utf-8')
                    }
                )
                print('✅ Новый админ создан')
            
            await session.commit()
            print('✅ Изменения сохранены в базе')
            
        except Exception as e:
            print(f'❌ Ошибка: {e}')
            await session.rollback()

asyncio.run(fix_admin())
"
else
    echo "❌ API контейнер не найден!"
fi

echo "8️⃣ Тестирование API..."
chmod +x test_api.sh
./test_api.sh

echo "✅ SSL исправление завершено!" 