#!/bin/bash

echo "🚀 Запуск продакшен версии с nginx на порту 80..."

# Остановить все контейнеры
echo "🛑 Остановка существующих контейнеров..."
docker-compose down

# Удалить старые образы (опционально)
echo "🧹 Очистка старых образов..."
docker system prune -f

# Запустить продакшен версию
echo "🏗️ Сборка и запуск продакшен контейнеров..."
docker-compose -f docker-compose.prod.yml up --build -d

# Показать статус
echo "📊 Статус контейнеров:"
docker-compose -f docker-compose.prod.yml ps

echo "✅ Продакшен версия запущена!"
echo "🌐 Сайт доступен по адресу: http://5.129.198.80"
echo "📱 API доступен по адресу: http://5.129.198.80/api"
echo "📚 Документация API: http://5.129.198.80/docs" 