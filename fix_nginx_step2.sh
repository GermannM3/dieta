#!/bin/bash

echo "🔧 Шаг 2: Исправление SSL конфигурации..."

echo "1️⃣ Проверка что nginx слушает на 443..."
docker exec dieta-nginx-1 netstat -tlnp

echo "2️⃣ Проверка конфига nginx..."
docker exec dieta-nginx-1 nginx -t

echo "3️⃣ Проверка SSL сертификатов в контейнере..."
docker exec dieta-nginx-1 ls -la /etc/letsencrypt/live/

echo "4️⃣ Создание исправленного SSL конфига..."
cat > nginx-ssl-working.conf << 'EOF'
upstream api {
    server api:8000;
}

upstream frontend {
    server frontend:80;
}

# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name tvoi-kalkulyator.ru www.tvoi-kalkulyator.ru твой-калькулятор.рф www.твой-калькулятор.рф localhost;
    return 301 https://$host$request_uri;
}

# HTTPS сервер
server {
    listen 443 ssl http2;
    server_name tvoi-kalkulyator.ru www.tvoi-kalkulyator.ru твой-калькулятор.рф www.твой-калькулятор.рф localhost;

    ssl_certificate     /etc/letsencrypt/live/tvoi-kalkulyator.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tvoi-kalkulyator.ru/privkey.pem;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;
    
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

echo "5️⃣ Перезапуск с исправленным конфигом..."
docker-compose -f docker-compose.minimal.yml down
docker-compose -f docker-compose.minimal.yml up -d

echo "6️⃣ Проверка что HTTPS работает..."
sleep 5
curl -I https://localhost:443

echo "✅ Шаг 2 завершен!" 