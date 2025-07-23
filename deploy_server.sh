#!/bin/bash

# Скрипт для развертывания и запуска Dieta Bot на сервере
# Использование: ./deploy_server.sh

set -e

echo "🚀 Начинаем развертывание Dieta Bot..."

# Проверяем, что мы в правильной директории
if [ ! -f "main.py" ]; then
    echo "❌ Ошибка: main.py не найден. Убедитесь, что вы в корневой папке проекта."
    exit 1
fi

# Останавливаем старые процессы
echo "🛑 Останавливаем старые процессы..."
pkill -f "main.py" || true
pkill -f "improved_api_server.py" || true
pkill -f "npm start" || true
pkill -f "nginx" || true

# Активируем виртуальное окружение
echo "📦 Активируем виртуальное окружение..."
source venv/bin/activate

# Очищаем кеш pip и обновляем его
echo "🧹 Очищаем кеш pip..."
pip cache purge || true
pip install --upgrade pip

# Устанавливаем/обновляем зависимости с принудительным разрешением конфликтов
echo "📥 Устанавливаем зависимости..."
pip install --no-cache-dir --force-reinstall -r requirements.txt

# Проверяем подключение к базе данных
echo "🔍 Проверяем подключение к базе данных..."
python test_db_connection.py

# Устанавливаем systemd сервис
echo "⚙️ Устанавливаем systemd сервис..."
cp dieta-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable dieta-bot.service

# Запускаем сервис
echo "🚀 Запускаем сервис..."
systemctl start dieta-bot.service

# Ждем немного для запуска
sleep 5

# Проверяем статус
echo "📊 Проверяем статус сервиса..."
systemctl status dieta-bot.service --no-pager

echo "✅ Развертывание завершено!"
echo ""
echo "📋 Полезные команды:"
echo "  Статус сервиса: systemctl status dieta-bot.service"
echo "  Остановить: systemctl stop dieta-bot.service"
echo "  Перезапустить: systemctl restart dieta-bot.service"
echo "  Логи: journalctl -u dieta-bot.service -f"
echo ""
echo "🌐 Проверьте доступность:"
echo "  API: http://5.129.198.80:8000/health"
echo "  Фронтенд: http://5.129.198.80:3000"
echo "  Бот: @tvoy_diet_bot" 