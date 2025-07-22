#!/bin/bash

echo "🚨 ЭКСТРЕННАЯ ОЧИСТКА ДИСКА!"

echo "1️⃣ ОСТАНОВКА ВСЕХ КОНТЕЙНЕРОВ..."
docker compose down
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.minimal.yml down

echo "2️⃣ ПОЛНАЯ ОЧИСТКА DOCKER..."
docker system prune -af --volumes
docker builder prune -af
docker image prune -af
docker container prune -af
docker network prune -af
docker volume prune -af

echo "3️⃣ УДАЛЕНИЕ ВСЕХ ОБРАЗОВ..."
docker rmi $(docker images -q) 2>/dev/null || true

echo "4️⃣ ОЧИСТКА КЭША APT..."
apt-get clean
apt-get autoremove -y
apt-get autoclean

echo "5️⃣ ОЧИСТКА ЛОГОВ..."
rm -rf /var/log/*.log
rm -rf /var/log/*.gz
rm -rf /var/log/journal/*
journalctl --vacuum-time=1d
journalctl --vacuum-size=100M

echo "6️⃣ ОЧИСТКА TEMP ФАЙЛОВ..."
rm -rf /tmp/*
rm -rf /var/tmp/*

echo "7️⃣ ОЧИСТКА DOCKER OVERLAY..."
rm -rf /var/lib/docker/overlay2/*

echo "8️⃣ ПРОВЕРКА МЕСТА..."
df -h

echo "9️⃣ ПЕРЕЗАПУСК DOCKER..."
systemctl restart docker

echo "🔟 ФИНАЛЬНАЯ ПРОВЕРКА..."
df -h

echo "✅ ЭКСТРЕННАЯ ОЧИСТКА ЗАВЕРШЕНА!" 