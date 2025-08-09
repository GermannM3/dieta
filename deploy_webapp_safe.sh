#!/bin/bash

echo "🚀 Безопасный деплой веб-приложения..."

# Проверяем структуру папок
echo "📁 Проверяем структуру папок..."
if [ ! -d "/opt/dieta" ]; then
    echo "❌ Папка /opt/dieta не найдена"
    exit 1
fi

if [ ! -d "/opt/dieta/calorie-love-tracker" ]; then
    echo "❌ Папка /opt/dieta/calorie-love-tracker не найдена"
    exit 1
fi

echo "✅ Структура папок корректна"

# Проверяем статус сервисов
echo "📊 Проверяем текущий статус сервисов..."
sudo systemctl status frontend --no-pager | head -5
sudo systemctl status nginx --no-pager | head -5

# Останавливаем сервисы
echo "📦 Останавливаем сервисы..."
sudo systemctl stop frontend
sudo systemctl stop nginx

# Обновляем код (только если есть изменения)
echo "📥 Проверяем обновления в git..."
cd /opt/dieta
git fetch origin
if [ "$(git rev-list HEAD...origin/main --count)" != "0" ]; then
    echo "🔄 Обновляем код..."
    git pull origin main
else
    echo "✅ Код уже актуален"
fi

# Переходим в папку веб-приложения
echo "📁 Переходим в папку веб-приложения..."
cd /opt/dieta/calorie-love-tracker

# Проверяем package.json
if [ ! -f "package.json" ]; then
    echo "❌ package.json не найден"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
npm install

# Собираем приложение
echo "🔨 Собираем приложение..."
npm run build

# Проверяем, что сборка прошла успешно
if [ ! -d "dist" ]; then
    echo "❌ Папка dist не создана после сборки"
    exit 1
fi

echo "✅ Сборка завершена успешно"

# Обновляем nginx конфигурацию (с резервной копией)
echo "⚙️ Обновляем nginx конфигурацию..."
if [ -f "/etc/nginx/sites-available/tvoi-kalkulyator" ]; then
    echo "📋 Создаем резервную копию старой конфигурации..."
    sudo cp /etc/nginx/sites-available/tvoi-kalkulyator /etc/nginx/sites-available/tvoi-kalkulyator.backup
fi

sudo cp /opt/dieta/nginx-prod.conf /etc/nginx/sites-available/tvoi-kalkulyator
sudo ln -sf /etc/nginx/sites-available/tvoi-kalkulyator /etc/nginx/sites-enabled/

# Проверяем конфигурацию nginx
echo "🔍 Проверяем nginx конфигурацию..."
if sudo nginx -t; then
    echo "✅ Nginx конфигурация корректна"
else
    echo "❌ Ошибка в nginx конфигурации"
    echo "🔄 Восстанавливаем резервную копию..."
    sudo cp /etc/nginx/sites-available/tvoi-kalkulyator.backup /etc/nginx/sites-available/tvoi-kalkulyator
    sudo nginx -t
    exit 1
fi

# Обновляем systemd сервис (если нужно)
echo "⚙️ Обновляем systemd сервис..."
sudo cp /opt/dieta/frontend.service /etc/systemd/system/
sudo systemctl daemon-reload

# Запускаем сервисы
echo "🚀 Запускаем сервисы..."
sudo systemctl start frontend
sudo systemctl start nginx

# Ждем немного для запуска
sleep 3

# Проверяем статус
echo "📊 Проверяем статус сервисов..."
if sudo systemctl is-active --quiet frontend; then
    echo "✅ Frontend сервис запущен"
else
    echo "❌ Frontend сервис не запущен"
    sudo systemctl status frontend --no-pager
fi

if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx сервис запущен"
else
    echo "❌ Nginx сервис не запущен"
    sudo systemctl status nginx --no-pager
fi

echo "✅ Деплой завершен!"
echo "🌐 Сайт должен быть доступен по адресам:"
echo "   - http://tvoi-kalkulyator.ru"
echo "   - http://твой-калькулятор.рф"
echo "   - http://5.129.198.80"

echo ""
echo "🔍 Для диагностики используйте:"
echo "   python3 /opt/dieta/diagnose_auth_issues.py" 