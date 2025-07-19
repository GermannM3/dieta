#!/bin/bash

echo "🔍 Тестирование DNS в контейнерах"
echo "================================"

# Тест 1: Проверка DNS в Python контейнере
echo "🐍 Тест DNS в Python контейнере..."
docker run --rm --dns 8.8.8.8 --dns 8.8.4.4 python:3.11-slim sh -c "
echo 'Проверка DNS...'
nslookup deb.debian.org
echo 'Проверка apt-get...'
apt-get update -qq && echo '✅ DNS работает!' || echo '❌ DNS не работает'
"

# Тест 2: Проверка DNS в Alpine контейнере
echo "🏔️ Тест DNS в Alpine контейнере..."
docker run --rm --dns 8.8.8.8 --dns 8.8.4.4 alpine:latest sh -c "
echo 'Проверка DNS...'
nslookup google.com
echo 'Проверка apk...'
apk update -q && echo '✅ DNS работает!' || echo '❌ DNS не работает'
"

echo "✅ Тестирование завершено!" 