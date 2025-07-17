#!/bin/bash
echo "🔧 Полное исправление проблем на сервере Timeweb"
echo "================================================="

# Переходим в правильную папку
echo "📂 Переход в папку /opt/dieta..."
cd /opt/dieta || { echo "❌ Папка /opt/dieta не найдена!"; exit 1; }

echo "📍 Текущая папка: $(pwd)"
echo "📋 Содержимое папки:"
ls -la

# Принудительно обновляем проект
echo "🔄 Принудительное обновление проекта..."
git fetch origin
git reset --hard origin/main
git pull origin main

echo "✅ Проект обновлен"

# Полная очистка Docker кэша
echo "🧹 Полная очистка Docker..."
docker system prune -a -f
docker volume prune -f

# Удаляем все образы проекта
echo "🗑️ Удаление старых образов..."
docker rmi $(docker images "dieta*" -q) 2>/dev/null || true
docker rmi $(docker images "*dieta*" -q) 2>/dev/null || true

# Проверяем что правильный Dockerfile.frontend
echo "📝 Проверка Dockerfile.frontend..."
if grep -q "npm ci --only=production" Dockerfile.frontend; then
    echo "❌ Найден старый Dockerfile.frontend, исправляем..."
    curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/Dockerfile.frontend
fi

# Проверяем содержимое Dockerfile.frontend
echo "🔍 Проверка команды npm в Dockerfile.frontend:"
grep -n "npm ci" Dockerfile.frontend || echo "Команда npm ci не найдена"

# Принудительная пересборка без кэша
echo "🔧 Принудительная пересборка всех контейнеров..."
docker-compose down --volumes --remove-orphans
docker-compose build --no-cache --pull

# Запуск контейнеров
echo "🚀 Запуск контейнеров..."
docker-compose up -d

# Ждем запуска
echo "⏳ Ожидание запуска контейнеров..."
sleep 30

# Проверяем статус
echo "📊 Статус контейнеров:"
docker-compose ps

# Проверяем логи
echo "📋 Логи API:"
docker-compose logs --tail=10 api

echo "📋 Логи Bot:"
docker-compose logs --tail=10 bot

echo "📋 Логи Frontend:"
docker-compose logs --tail=10 frontend

# Проверяем health check
echo "🏥 Проверка health check API:"
curl -f http://localhost:8000/health || echo "❌ API не отвечает"

echo "✅ Исправление завершено!"
echo ""
echo "🌐 Доступные сервисы:"
echo "- API: http://5.129.198.80:8000"
echo "- Health: http://5.129.198.80:8000/health"
echo "- Docs: http://5.129.198.80:8000/docs"
echo "- Frontend: http://5.129.198.80:3000" 