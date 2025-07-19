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

# Исправляем админа
chmod +x fix_admin_docker.sh
./fix_admin_docker.sh

echo "✅ Обновление завершено!" 