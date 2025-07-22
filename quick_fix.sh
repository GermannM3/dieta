#!/bin/bash

echo "🚀 Быстрое исправление проблем с Docker..."

# Останавливаем контейнеры
echo "🛑 Останавливаем контейнеры..."
docker-compose down

# Очищаем Docker (для старого Docker)
echo "🧹 Очищаем Docker..."
docker container prune -f
docker image prune -f
docker volume prune -f
docker network prune -f

# Пересобираем без кэша
echo "🔨 Пересобираем контейнеры..."
docker-compose build --no-cache

# Запускаем
echo "🚀 Запускаем контейнеры..."
docker-compose up -d

# Ждем запуска
echo "⏳ Ждем запуска сервисов..."
sleep 30

# Проверяем статус
echo "🔍 Проверяем статус..."
docker-compose ps

# Проверяем API
echo "🔍 Проверяем API..."
curl -f http://5.129.198.80:8000/health || echo "❌ API не отвечает"

# Проверяем домены
echo "🔍 Проверяем домены..."
curl -f -k https://твой-калькулятор.рф || echo "❌ Домен твой-калькулятор.рф не отвечает"
curl -f -k https://tvoi-kalkulyator.ru || echo "❌ Домен tvoi-kalkulyator.ru не отвечает"

echo "✅ Исправление завершено!" 