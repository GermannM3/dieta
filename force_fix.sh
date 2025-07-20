#!/bin/bash

echo "💪 Принудительное исправление сервера..."

echo "1️⃣ Принудительный сброс всех изменений..."
git reset --hard HEAD
git clean -fd
git stash -u

echo "2️⃣ Удаление конфликтующих файлов..."
rm -rf nginx-ssl-working.conf
rm -f quick_fix.sh
rm -f fix_server.sh

echo "3️⃣ Принудительное подтягивание..."
git fetch origin
git reset --hard origin/main

echo "4️⃣ Проверка файлов..."
ls -la fix_server.sh

echo "5️⃣ Остановка контейнеров..."
docker-compose -f docker-compose.minimal.yml down 2>/dev/null
docker-compose down 2>/dev/null

echo "6️⃣ Создание nginx конфига..."
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

echo "7️⃣ Запуск контейнеров..."
docker-compose -f docker-compose.minimal.yml up -d

echo "8️⃣ Ожидание запуска..."
sleep 20

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

echo "🔟 Тестирование API..."
chmod +x test_api.sh
./test_api.sh

echo "1️⃣1️⃣ Проверка статуса..."
docker ps

echo "✅ Принудительное исправление завершено!" 