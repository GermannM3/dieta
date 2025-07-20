#!/bin/bash

echo "🔍 Проверка портов на сервере..."

echo "📡 Проверяем какие порты слушаются:"
sudo netstat -tlnp | grep -E ':(80|443)'
echo ""

echo "🌐 Проверяем локальный HTTP:"
curl -I http://localhost:80
echo ""

echo "🔒 Проверяем локальный HTTPS:"
curl -I http://localhost:443
echo ""

echo "🔧 Проверяем статус контейнеров:"
docker ps
echo ""

echo "📋 Проверяем логи nginx:"
docker logs $(docker ps -q --filter "name=nginx") --tail 20
echo ""

echo "✅ Проверка завершена!" 