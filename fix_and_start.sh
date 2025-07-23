#!/bin/bash

# Быстрое исправление и запуск Dieta Bot
# Использование: ./fix_and_start.sh

set -e

echo "🚀 Быстрое исправление и запуск Dieta Bot..."

# Проверяем, что мы в правильной директории
if [ ! -f "main.py" ]; then
    echo "❌ Ошибка: main.py не найден. Убедитесь, что вы в корневой папке проекта."
    exit 1
fi

# Останавливаем все процессы
echo "🛑 Останавливаем все процессы..."
pkill -f "main.py" || true
pkill -f "improved_api_server.py" || true
pkill -f "npm start" || true
pkill -f "nginx" || true

# Активируем виртуальное окружение
echo "📦 Активируем виртуальное окружение..."
source venv/bin/activate

# Исправляем зависимости
echo "🔧 Исправляем зависимости..."
./fix_dependencies.sh

# Создаем папку для логов
mkdir -p logs

# Проверяем конфигурацию
echo "🔍 Проверяем конфигурацию..."
python test_db_connection.py

# Делаем скрипт исполняемым
chmod +x start_production.sh

# Запускаем все сервисы
echo "🚀 Запускаем все сервисы..."
./start_production.sh

echo ""
echo "✅ Диета Бот запущен!"
echo ""
echo "🌐 Доступные адреса:"
echo "  Веб-сайт: http://tvoi-kalkulyator.ru"
echo "  Альтернативный домен: http://твой-калькулятор.рф"
echo "  API: http://tvoi-kalkulyator.ru/api/health"
echo ""
echo "📊 Проверка статуса:"
echo "  systemctl status dieta-bot.service"
echo ""
echo "📋 Логи:"
echo "  journalctl -u dieta-bot.service -f" 