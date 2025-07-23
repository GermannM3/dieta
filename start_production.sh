#!/bin/bash

# Скрипт для запуска Dieta Bot в продакшене
# Использование: ./start_production.sh

set -e

echo "🚀 Запуск Dieta Bot в продакшене..."

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

# Проверяем зависимости
echo "🔍 Проверяем зависимости..."
python quick_server_fix.py

# Запускаем API сервер на порту 8000
echo "🌐 Запускаем API сервер на порту 8000..."
nohup python improved_api_server.py > logs/api.log 2>&1 &
API_PID=$!
echo "✅ API сервер запущен (PID: $API_PID)"

# Ждем запуска API
sleep 3

# Проверяем API
echo "🔍 Проверяем API сервер..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API сервер работает"
else
    echo "❌ API сервер не отвечает"
    exit 1
fi

# Переходим в папку фронтенда
echo "🎨 Запускаем фронтенд..."
cd calorie-love-tracker

# Устанавливаем зависимости если нужно
if [ ! -d "node_modules" ]; then
    echo "📦 Устанавливаем зависимости фронтенда..."
    npm install
fi

# Собираем проект
echo "🔨 Собираем фронтенд..."
npm run build

# Запускаем фронтенд на порту 3000
echo "🌐 Запускаем фронтенд на порту 3000..."
nohup npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Фронтенд запущен (PID: $FRONTEND_PID)"

# Возвращаемся в корневую папку
cd ..

# Ждем запуска фронтенда
sleep 5

# Проверяем фронтенд
echo "🔍 Проверяем фронтенд..."
if curl -s -I http://localhost:3000 | grep -q "200 OK"; then
    echo "✅ Фронтенд работает"
else
    echo "❌ Фронтенд не отвечает"
    exit 1
fi

# Настраиваем nginx
echo "🔧 Настраиваем nginx..."
cp nginx-prod.conf /etc/nginx/sites-available/tvoi-kalkulyator
ln -sf /etc/nginx/sites-available/tvoi-kalkulyator /etc/nginx/sites-enabled/

# Удаляем дефолтный сайт
rm -f /etc/nginx/sites-enabled/default

# Проверяем конфигурацию nginx
echo "🔍 Проверяем конфигурацию nginx..."
nginx -t

# Перезапускаем nginx
echo "🔄 Перезапускаем nginx..."
systemctl restart nginx

# Запускаем бота
echo "🤖 Запускаем Telegram бота..."
nohup python main.py > logs/bot.log 2>&1 &
BOT_PID=$!
echo "✅ Бот запущен (PID: $BOT_PID)"

# Сохраняем PID в файл
echo $API_PID > logs/api.pid
echo $FRONTEND_PID > logs/frontend.pid
echo $BOT_PID > logs/bot.pid

# Ждем немного
sleep 3

# Финальная проверка
echo "🔍 Финальная проверка..."
echo "API (порт 8000): $(curl -s http://localhost:8000/health || echo 'НЕ РАБОТАЕТ')"
echo "Фронтенд (порт 3000): $(curl -s -I http://localhost:3000 | head -1 || echo 'НЕ РАБОТАЕТ')"
echo "Nginx (порт 80): $(curl -s -I http://localhost | head -1 || echo 'НЕ РАБОТАЕТ')"

echo ""
echo "✅ Все сервисы запущены!"
echo ""
echo "📋 Информация:"
echo "  API сервер: http://localhost:8000"
echo "  Фронтенд: http://localhost:3000"
echo "  Веб-сайт: http://tvoi-kalkulyator.ru"
echo "  Альтернативный домен: http://твой-калькулятор.рф"
echo ""
echo "📊 Логи:"
echo "  API: tail -f logs/api.log"
echo "  Фронтенд: tail -f logs/frontend.log"
echo "  Бот: tail -f logs/bot.log"
echo "  Nginx: tail -f /var/log/nginx/tvoi-kalkulyator.error.log"
echo ""
echo "🛑 Для остановки: ./stop_all.sh" 