#!/bin/bash

echo "🔄 Принудительное обновление файлов..."

cd /opt/dieta

# Сохраняем текущие изменения
git stash

# Принудительно подтягиваем изменения
git fetch origin
git reset --hard origin/main

# Перезапускаем стек
docker-compose -f docker-compose.fresh.yml down
docker-compose -f docker-compose.fresh.yml up -d

# Ждем запуска контейнеров
sleep 10

# Исправляем админа
echo "🔧 Исправляем админа..."
source venv/bin/activate
python3 fix_admin_simple.py

echo "✅ Обновление завершено!"
echo "🌐 Проверьте сайты:"
echo "   https://tvoi-kalkulyator.ru"
echo "   https://твой-калькулятор.рф" 