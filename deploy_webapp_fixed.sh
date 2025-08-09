#!/bin/bash

echo "🚀 Деплой веб-приложения с исправленными настройками..."

# Останавливаем сервисы
echo "📦 Останавливаем сервисы..."
sudo systemctl stop frontend
sudo systemctl stop nginx

# Обновляем код (git репозиторий уже в /opt/dieta)
echo "📥 Обновляем код..."
cd /opt/dieta
git pull origin main

# Переходим в папку веб-приложения
echo "📁 Переходим в папку веб-приложения..."
cd /opt/dieta/calorie-love-tracker

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
npm install

# Собираем приложение
echo "🔨 Собираем приложение..."
npm run build

# Копируем обновленную nginx конфигурацию
echo "⚙️ Обновляем nginx конфигурацию..."
sudo cp /opt/dieta/nginx-prod.conf /etc/nginx/sites-available/tvoi-kalkulyator
sudo ln -sf /etc/nginx/sites-available/tvoi-kalkulyator /etc/nginx/sites-enabled/

# Проверяем конфигурацию nginx
echo "🔍 Проверяем nginx конфигурацию..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx конфигурация корректна"
else
    echo "❌ Ошибка в nginx конфигурации"
    exit 1
fi

# Запускаем сервисы
echo "🚀 Запускаем сервисы..."
sudo systemctl start frontend
sudo systemctl start nginx

# Проверяем статус
echo "📊 Проверяем статус сервисов..."
sudo systemctl status frontend --no-pager
sudo systemctl status nginx --no-pager

echo "✅ Деплой завершен!"
echo "🌐 Сайт доступен по адресам:"
echo "   - http://tvoi-kalkulyator.ru"
echo "   - http://твой-калькулятор.рф"
echo "   - http://5.129.198.80" 