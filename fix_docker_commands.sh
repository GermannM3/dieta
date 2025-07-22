#!/bin/bash

echo "🔧 ИСПРАВЛЕНИЕ КОМАНД DOCKER COMPOSE V2!"

echo "1️⃣ Остановка всех контейнеров..."
docker compose down

echo "2️⃣ Очистка Docker (правильные команды)..."
docker system prune -af
docker volume prune -af
docker builder prune -af

echo "3️⃣ Очистка кэша apt..."
apt-get clean
apt-get autoremove -y

echo "4️⃣ Очистка логов..."
rm -rf /var/log/*.log
rm -rf /var/log/*.gz
journalctl --vacuum-time=1d

echo "5️⃣ Проверка места..."
df -h

echo "6️⃣ Получение исправлений..."
git pull

echo "7️⃣ Сборка и запуск..."
docker compose build --no-cache
docker compose up -d

echo "8️⃣ Проверка статуса..."
sleep 10
docker compose ps

echo "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!" 