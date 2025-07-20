#!/bin/bash

echo "🔍 Детальная проверка nginx контейнера..."

echo "📋 Статус контейнеров:"
docker ps -a | grep nginx
echo ""

echo "📄 Логи nginx контейнера:"
docker logs dieta-nginx-1 --tail 50
echo ""

echo "🔧 Проверка конфига nginx:"
docker exec dieta-nginx-1 nginx -t 2>&1
echo ""

echo "📁 Проверка SSL сертификатов в контейнере:"
docker exec dieta-nginx-1 ls -la /etc/letsencrypt/live/ 2>&1
echo ""

echo "🌐 Проверка что nginx слушает внутри контейнера:"
docker exec dieta-nginx-1 netstat -tlnp 2>&1
echo ""

echo "✅ Проверка завершена!" 