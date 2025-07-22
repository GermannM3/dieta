#!/bin/bash

echo "🧹 ОЧИСТКА МЕСТА НА СЕРВЕРЕ..."

echo "1️⃣ Остановка всех контейнеров..."
docker-compose down
docker-compose -f docker-compose.production.yml down

echo "2️⃣ Очистка Docker..."
docker system prune -af --volumes
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

echo "✅ Очистка завершена!" 