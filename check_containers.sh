#!/bin/bash

echo "🔍 Проверка статуса контейнеров..."

echo "📋 Все контейнеры:"
docker ps -a

echo ""
echo "📋 Запущенные контейнеры:"
docker ps

echo ""
echo "📄 Логи API контейнера:"
docker logs $(docker ps -q --filter "name=api") --tail 10 2>/dev/null || echo "API контейнер не найден"

echo ""
echo "📄 Логи nginx контейнера:"
docker logs $(docker ps -q --filter "name=nginx") --tail 10 2>/dev/null || echo "Nginx контейнер не найден"

echo ""
echo "🌐 Проверка портов:"
sudo netstat -tlnp | grep -E ':(80|443|8000)'

echo "✅ Проверка завершена!" 