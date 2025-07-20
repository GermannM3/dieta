#!/bin/bash

echo "🔧 Диагностика и исправление nginx..."

echo "1️⃣ Проверка логов nginx..."
docker logs dieta-nginx-1 2>&1 | tail -20

echo "2️⃣ Проверка конфига nginx..."
cat nginx-ssl.conf

echo "3️⃣ Остановка nginx..."
docker stop dieta-nginx-1 2>/dev/null
docker rm dieta-nginx-1 2>/dev/null

echo "4️⃣ Создание простого nginx конфига..."
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

echo "5️⃣ Запуск nginx..."
docker-compose -f docker-compose.minimal.yml up -d nginx

echo "6️⃣ Ожидание запуска..."
sleep 15

echo "7️⃣ Проверка статуса nginx..."
docker ps | grep nginx

echo "8️⃣ Тестирование nginx..."
curl -I http://5.129.198.80/api/docs 2>/dev/null | head -1

echo "9️⃣ Проверка логов после запуска..."
docker logs dieta-nginx-1 2>&1 | tail -10

echo "✅ Диагностика nginx завершена!" 