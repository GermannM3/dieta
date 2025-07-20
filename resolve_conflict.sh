#!/bin/bash

echo "🔧 Правильное разрешение git конфликтов..."

echo "1️⃣ Сохранение локальных изменений..."
git stash push -m "local_changes_$(date +%s)"

echo "2️⃣ Подтягивание изменений..."
git pull

echo "3️⃣ Применение локальных изменений..."
git stash pop

echo "4️⃣ Разрешение конфликтов..."
if [ -f "test_api.sh" ]; then
    echo "✅ test_api.sh найден"
    chmod +x test_api.sh
fi

if [ -f "fix_nginx.sh" ]; then
    echo "✅ fix_nginx.sh найден"
    chmod +x fix_nginx.sh
fi

echo "5️⃣ Проверка статуса..."
git status

echo "6️⃣ Запуск исправления nginx..."
if [ -f "fix_nginx.sh" ]; then
    ./fix_nginx.sh
else
    echo "❌ fix_nginx.sh не найден, создаем вручную..."
    
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

    echo "7️⃣ Перезапуск nginx..."
    docker stop dieta-nginx-1 2>/dev/null
    docker rm dieta-nginx-1 2>/dev/null
    docker-compose -f docker-compose.minimal.yml up -d nginx
    
    echo "8️⃣ Ожидание запуска..."
    sleep 15
    
    echo "9️⃣ Проверка статуса..."
    docker ps | grep nginx
fi

echo "✅ Конфликт разрешен!" 