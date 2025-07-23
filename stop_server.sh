#!/bin/bash

echo "🛑 Остановка всех сервисов диет-бота"
echo "===================================="

# Останавливаем все процессы
pkill -f "python.*main.py" || true
pkill -f "python.*improved_api_server.py" || true
pkill -f "npm.*start" || true
pkill -f "nginx" || true

echo "✅ Все сервисы остановлены!" 