#!/bin/bash

echo "🔧 Пошаговое исправление nginx..."

echo "1️⃣ Остановка всех контейнеров..."
docker-compose -f docker-compose.minimal.yml down

echo "2️⃣ Проверка SSL сертификатов..."
sudo ls -la /etc/letsencrypt/live/tvoi-kalkulyator.ru/

echo "3️⃣ Создание простого nginx конфига без SSL..."
cat > nginx-simple-no-ssl.conf << 'EOF'
upstream api {
    server api:8000;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api/ {
        proxy_pass http://api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

echo "4️⃣ Запуск только с HTTP..."
docker-compose -f docker-compose.minimal.yml up -d

echo "5️⃣ Проверка что HTTP работает..."
sleep 5
curl -I http://localhost:80

echo "6️⃣ Проверка статуса контейнеров..."
docker ps

echo "✅ Шаг 1 завершен!" 