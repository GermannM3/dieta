#!/bin/bash

echo "🔍 Проверка SSL конфигурации..."

echo "📋 Статус контейнеров:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "📄 Логи nginx контейнера:"
docker logs dieta-nginx-1 --tail 20
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

echo "📄 Проверка конфига внутри контейнера:"
docker exec dieta-nginx-1 cat /etc/nginx/conf.d/default.conf
echo ""

echo "🔍 Проверка SSL сертификатов на хосте:"
sudo ls -la /etc/letsencrypt/live/
echo ""

echo "✅ Проверка завершена!" 