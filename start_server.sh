#!/bin/bash

echo "🤖 Запуск диет-бота на сервере"
echo "================================"

# Проверяем что venv активирован
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Виртуальное окружение не активировано!"
    echo "Активируйте venv: source venv/bin/activate"
    exit 1
fi

echo "✅ Виртуальное окружение активировано: $VIRTUAL_ENV"

# Останавливаем старые процессы
echo "🛑 Остановка старых процессов..."
pkill -f "python.*main.py" || true
pkill -f "python.*improved_api_server.py" || true
pkill -f "npm.*start" || true
pkill -f "nginx" || true

sleep 2

# Запускаем все сервисы
echo "🚀 Запуск всех сервисов..."
python start_all_services.py

echo "✅ Все сервисы запущены!"
echo "📱 Бот: @tvoy_diet_bot"
echo "🌐 Сайт: http://5.129.198.80"
echo "📊 API: http://5.129.198.80:8000/docs" 