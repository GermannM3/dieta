#!/bin/bash

echo "🔍 ДЕТАЛЬНАЯ ДИАГНОСТИКА API КОНТЕЙНЕРА..."

echo "1️⃣ Проверка всех контейнеров..."
docker ps -a

echo "2️⃣ Проверка образов..."
docker images | grep api

echo "3️⃣ Проверка логов API контейнера..."
if docker ps -q --filter "name=dieta-api-1" | grep -q .; then
    echo "✅ Контейнер dieta-api-1 найден и запущен"
    docker logs dieta-api-1 2>&1 | tail -20
else
    echo "❌ Контейнер dieta-api-1 не найден или не запущен"
    
    echo "4️⃣ Поиск всех контейнеров с 'api' в имени..."
    docker ps -a --filter "name=api"
    
    echo "5️⃣ Проверка docker-compose статуса..."
    docker-compose -f docker-compose.minimal.yml ps
fi

echo "6️⃣ Проверка сети..."
docker network ls
docker network inspect dieta_app-network 2>/dev/null || echo "❌ Сеть dieta_app-network не найдена"

echo "7️⃣ Проверка переменных окружения..."
if [ -f ".env" ]; then
    echo "✅ .env файл найден"
    grep -E "(DATABASE|API|BOT)" .env | head -5
else
    echo "❌ .env файл не найден"
fi

echo "8️⃣ Попытка запуска API контейнера..."
docker-compose -f docker-compose.minimal.yml up -d api

echo "9️⃣ Ожидание запуска..."
sleep 10

echo "🔟 Финальная проверка..."
docker ps | grep api

echo "1️⃣1️⃣ Проверка логов после запуска..."
if docker ps -q --filter "name=dieta-api-1" | grep -q .; then
    docker logs dieta-api-1 2>&1 | tail -10
else
    echo "❌ API контейнер все еще не запущен"
    echo "🔧 Попытка пересборки..."
    docker-compose -f docker-compose.minimal.yml build --no-cache api
    docker-compose -f docker-compose.minimal.yml up -d api
    sleep 15
    docker ps | grep api
fi

echo "✅ Диагностика завершена!" 