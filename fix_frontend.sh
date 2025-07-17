#!/bin/bash
echo "🔧 Исправление проблемы с фронтендом"
echo "==================================="

cd /opt/dieta

# Скачиваем исправленный Dockerfile.frontend
echo "📥 Скачивание исправленного Dockerfile.frontend..."
curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/Dockerfile.frontend

# Проверяем что файл правильный
echo "📋 Проверка Dockerfile.frontend..."
grep -n "npm ci" Dockerfile.frontend

# Останавливаем контейнеры
echo "🛑 Остановка контейнеров..."
docker-compose down

# Удаляем старые образы
echo "🧹 Очистка старых образов..."
docker rmi dieta_frontend 2>/dev/null || true

# Пересобираем фронтенд
echo "🔧 Пересборка фронтенда..."
docker-compose build --no-cache frontend

# Запускаем все сервисы
echo "🚀 Запуск сервисов..."
docker-compose up -d

# Проверяем статус
echo "📊 Статус сервисов:"
docker-compose ps

echo ""
echo "✅ Исправление завершено!"
echo "📝 Проверьте логи: docker-compose logs frontend" 