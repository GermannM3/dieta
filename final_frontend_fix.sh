#!/bin/bash

echo "🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ FRONTEND 502 ОШИБКИ!"

echo "1️⃣ ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ..."
docker ps

echo "2️⃣ ПРОВЕРКА ЛОГОВ FRONTEND..."
docker-compose logs frontend

echo "3️⃣ ПРОВЕРКА ЛОГОВ NGINX..."
docker-compose logs nginx

echo "4️⃣ СОЗДАНИЕ ПРАВИЛЬНОГО NGINX КОНФИГА..."
cat > nginx-correct.conf << 'EOF'
# Основной сервер для доменов с SSL
server {
    listen 80;
    server_name tvoi-kalkulyator.ru www.tvoi-kalkulyator.ru;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tvoi-kalkulyator.ru www.tvoi-kalkulyator.ru;

    ssl_certificate /etc/letsencrypt/live/tvoi-kalkulyator.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tvoi-kalkulyator.ru/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

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

    # Frontend - правильный порт 80
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Frontend - правильный порт 80
    location / {
        proxy_pass http://frontend:80;
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

echo "5️⃣ ПРИМЕНЕНИЕ NGINX КОНФИГА..."
docker cp nginx-correct.conf dieta-nginx-1:/etc/nginx/conf.d/default.conf

echo "6️⃣ ПЕРЕЗАПУСК NGINX..."
docker-compose -f docker-compose.minimal.yml restart nginx

echo "7️⃣ ОЖИДАНИЕ ЗАПУСКА..."
sleep 10

echo "8️⃣ ПРОВЕРКА NGINX КОНФИГА..."
docker exec dieta-nginx-1 nginx -t

echo "9️⃣ ТЕСТИРОВАНИЕ FRONTEND ВНУТРИ КОНТЕЙНЕРА..."
docker exec dieta-frontend-1 curl -I http://localhost:80 2>/dev/null | head -1

echo "🔟 ТЕСТИРОВАНИЕ СВЯЗЕЙ..."
echo "🔍 Тест HTTP Frontend по IP..."
curl -I http://5.129.198.80/ 2>/dev/null | head -1

echo "🔍 Тест HTTPS Frontend по домену..."
curl -I https://tvoi-kalkulyator.ru/ -k 2>/dev/null | head -1

echo "🔍 Тест HTTP API по IP..."
curl -X POST http://5.129.198.80/api/search_food \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  2>/dev/null | head -1

echo "🔍 Тест HTTPS API по домену..."
curl -X POST https://tvoi-kalkulyator.ru/api/search_food \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  -k 2>/dev/null | head -1

echo "1️⃣1️⃣ ФИНАЛЬНАЯ ПРОВЕРКА..."
docker ps

echo "✅ ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ FRONTEND ЗАВЕРШЕНО!"
echo ""
echo "🌐 Сайты должны быть доступны:"
echo "   HTTP:  http://5.129.198.80"
echo "   HTTPS: https://tvoi-kalkulyator.ru"
echo ""
echo "🔧 API эндпоинты:"
echo "   http://5.129.198.80/api/search_food"
echo "   http://5.129.198.80/api/auth/login"
echo ""
echo "👤 Админ: germannm@vk.com / Germ@nnM3" 