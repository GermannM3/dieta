#!/bin/bash

echo "🔄 Перезапуск всех сервисов..."

echo "1️⃣ Остановка всех контейнеров..."
docker-compose -f docker-compose.minimal.yml down

echo "2️⃣ Очистка..."
docker system prune -f

echo "3️⃣ Запуск контейнеров..."
docker-compose -f docker-compose.minimal.yml up -d

echo "4️⃣ Ожидание запуска..."
sleep 10

echo "5️⃣ Проверка статуса..."
docker ps

echo "6️⃣ Проверка API..."
curl -I https://tvoi-kalkulyator.ru/docs

echo "✅ Перезапуск завершен!" 