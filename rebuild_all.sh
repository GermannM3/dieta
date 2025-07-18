#!/bin/bash

echo "🚀 Полная пересборка системы..."
echo "=================================================="

# Остановить все контейнеры
echo "🛑 Остановка всех контейнеров..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

# Удалить все образы
echo "🗑️ Удаление всех образов..."
docker rmi $(docker images -q) -f 2>/dev/null || true

# Удалить все volumes
echo "🗑️ Удаление всех volumes..."
docker volume rm $(docker volume ls -q) -f 2>/dev/null || true

# Удалить все networks
echo "🗑️ Удаление всех networks..."
docker network rm $(docker network ls -q) -f 2>/dev/null || true

# Полная очистка системы
echo "🧹 Полная очистка Docker..."
docker system prune -a -f --volumes

# Получить последние изменения
echo "📥 Получение последних изменений..."
git pull

# Запустить с нуля (без кэша)
echo "🏗️ Сборка и запуск с нуля..."
docker-compose -f docker-compose.fresh.yml build --no-cache
docker-compose -f docker-compose.fresh.yml up -d

# Проверить статус
echo "📊 Статус контейнеров:"
docker-compose -f docker-compose.fresh.yml ps

echo "✅ Пересборка завершена!"
echo "🌐 Сайт: http://5.129.198.80"
echo "📱 API: http://5.129.198.80/api" 