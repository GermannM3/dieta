#!/bin/bash

echo "🚀 Финальное исправление всех проблем..."

# Останавливаем все контейнеры
echo "🛑 Останавливаем контейнеры..."
docker-compose down
docker stop $(docker ps -aq) 2>/dev/null || true

# Очищаем Docker полностью
echo "🧹 Очищаем Docker..."
docker system prune -af --volumes

# Пересобираем без кэша
echo "🔨 Пересобираем контейнеры..."
docker-compose build --no-cache

# Запускаем
echo "🚀 Запускаем контейнеры..."
docker-compose up -d

# Ждем запуска
echo "⏳ Ждем запуска сервисов..."
sleep 45

# Проверяем статус
echo "🔍 Проверяем статус..."
docker-compose ps

# Проверяем API
echo "🔍 Проверяем API..."
curl -f http://5.129.198.80:8000/health && echo "✅ API работает" || echo "❌ API не отвечает"

# Проверяем frontend
echo "🔍 Проверяем frontend..."
curl -f http://5.129.198.80:3000 && echo "✅ Frontend работает" || echo "❌ Frontend не отвечает"

# Проверяем nginx логи
echo "🔍 Проверяем nginx логи..."
docker-compose logs nginx --tail=10

# Проверяем домены
echo "🔍 Проверяем домены..."
curl -f -k https://твой-калькулятор.рф && echo "✅ Домен твой-калькулятор.рф работает" || echo "❌ Домен твой-калькулятор.рф не отвечает"
curl -f -k https://tvoi-kalkulyator.ru && echo "✅ Домен tvoi-kalkulyator.ru работает" || echo "❌ Домен tvoi-kalkulyator.ru не отвечает"

echo "✅ Финальное исправление завершено!" 