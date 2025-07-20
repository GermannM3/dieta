#!/bin/bash

echo "🔍 Детальная отладка nginx..."

echo "📋 Статус всех контейнеров:"
docker ps -a
echo ""

echo "📄 Логи nginx контейнера:"
docker logs dieta-nginx-1 --tail 20
echo ""

echo "🔧 Проверка конфига nginx:"
docker exec dieta-nginx-1 nginx -t 2>&1
echo ""

echo "📁 Проверка SSL сертификатов:"
sudo ls -la /etc/letsencrypt/live/
echo ""

echo "🌐 Проверка портов на хосте:"
sudo netstat -tlnp | grep -E ':(80|443)'
echo ""

echo "🔍 Проверка что nginx слушает внутри контейнера:"
docker exec dieta-nginx-1 netstat -tlnp 2>&1
echo ""

echo "📄 Проверка конфига внутри контейнера:"
docker exec dieta-nginx-1 cat /etc/nginx/conf.d/default.conf
echo ""

echo "✅ Отладка завершена!" 