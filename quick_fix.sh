#!/bin/bash

echo "🚀 Быстрое исправление всех проблем..."

echo "1️⃣ Очистка конфликтующих файлов..."
rm -f nginx-ssl-working.conf

echo "2️⃣ Подтягивание изменений..."
git pull

echo "3️⃣ Перезапуск контейнеров..."
docker-compose -f docker-compose.minimal.yml down
docker-compose -f docker-compose.minimal.yml up -d

echo "4️⃣ Ожидание запуска..."
sleep 10

echo "5️⃣ Исправление админа..."
docker exec $(docker ps -q --filter "name=api") python3 -c "
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

echo "6️⃣ Тестирование API..."
./test_api.sh

echo "✅ Все исправления завершены!" 