#!/bin/bash

# Автоматический деплой Твой Диетолог на сервер
# Скачивает последнюю версию с GitHub и разворачивает бота + веб-приложение

set -e  # Остановка при любой ошибке

echo "=========================================="
echo "   АВТОМАТИЧЕСКИЙ ДЕПЛОЙ ТВОЙ ДИЕТОЛОГ"
echo "=========================================="
echo

# Переменные
REPO_URL="https://github.com/GermannM3/dieta.git"
APP_DIR="/opt/dieta"
WEBAPP_DIR="/opt/diet-webapp"
BOT_NAME="dieta-bot"
API_NAME="dieta-api"
WEBAPP_NAME="diet-webapp"

echo "🔧 Настройка переменных окружения..."

# Создаем .env файл если его нет
if [ ! -f "$APP_DIR/.env" ]; then
    echo "⚙️ Создание файла конфигурации..."
    cat > "$APP_DIR/.env" << 'EOF'
# Telegram Bot Configuration
TG_TOKEN=your_telegram_bot_token_from_botfather
ADMIN_ID=your_telegram_id_number

# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# AI API Keys
GIGACHAT_CLIENT_ID=your_gigachat_client_id
GIGACHAT_AUTH_KEY=your_gigachat_auth_key
GIGACHAT_ACCESS_TOKEN=your_gigachat_access_token
MISTRAL_API_KEY=your_mistral_api_key
CALORIE_NINJAS_API_KEY=your_calorie_ninjas_api_key

# Optional Settings
LOG_LEVEL=INFO
API_PORT=8000
EOF
    echo "❌ ВНИМАНИЕ! Отредактируйте файл $APP_DIR/.env с вашими ключами"
    echo "Затем запустите скрипт снова"
    exit 1
fi

echo "📦 Остановка старых контейнеров..."
docker stop $BOT_NAME $API_NAME $WEBAPP_NAME 2>/dev/null || true
docker rm $BOT_NAME $API_NAME $WEBAPP_NAME 2>/dev/null || true

echo "📂 Подготовка директорий..."
mkdir -p $APP_DIR
mkdir -p $WEBAPP_DIR

echo "📥 Скачивание последней версии с GitHub..."
if [ -d "$APP_DIR/.git" ]; then
    cd $APP_DIR
    git pull origin main
else
    rm -rf $APP_DIR/*
    git clone $REPO_URL $APP_DIR
    cd $APP_DIR
fi

echo "🐳 Сборка Docker образов..."

# Сборка основного образа для бота и API
docker build -t dieta-app:latest .

# Сборка веб-приложения
cd calorie-love-tracker
cp -r * $WEBAPP_DIR/
cd $WEBAPP_DIR

docker build -t diet-webapp:latest \
  --build-arg VITE_API_URL=http://$(hostname -I | awk '{print $1}'):8000 \
  --build-arg VITE_APP_TITLE="Твой Диетолог - Персональный ИИ-помощник" \
  --build-arg VITE_APP_DESCRIPTION="Продвинутый телеграм-бот с личным диетологом" \
  --build-arg VITE_TELEGRAM_BOT_USERNAME=@tvoy_diet_bot \
  .

echo "🚀 Запуск сервисов..."

# Запуск API сервера
docker run -d \
  --name $API_NAME \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file $APP_DIR/.env \
  -v $APP_DIR/logs:/app/logs \
  dieta-app:latest python improved_api_server.py

# Ждем запуска API
sleep 5

# Запуск Telegram бота
docker run -d \
  --name $BOT_NAME \
  --restart unless-stopped \
  --env-file $APP_DIR/.env \
  -e API_URL=http://$(hostname -I | awk '{print $1}'):8000 \
  -v $APP_DIR/logs:/app/logs \
  --depends-on $API_NAME \
  dieta-app:latest python main.py

# Запуск веб-приложения
docker run -d \
  --name $WEBAPP_NAME \
  --restart unless-stopped \
  -p 3000:3000 \
  diet-webapp:latest

echo "🌐 Настройка nginx..."

# Создаем конфигурацию nginx
cat > /etc/nginx/sites-available/dieta << 'EOL'
server {
    listen 80 default_server;
    server_name _;
    
    # Веб-приложение
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API сервер
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Документация API
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOL

# Удаляем конфликтующие конфигурации
rm -f /etc/nginx/sites-enabled/default
rm -f /etc/nginx/sites-enabled/webapp

# Активируем новую конфигурацию
ln -sf /etc/nginx/sites-available/dieta /etc/nginx/sites-enabled/dieta

# Тестируем и перезагружаем nginx
nginx -t && systemctl reload nginx

echo "✅ Проверка статуса сервисов..."
sleep 3

echo "Статус контейнеров:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo
echo "Логи API сервера:"
docker logs $API_NAME --tail 5

echo
echo "Логи Telegram бота:"
docker logs $BOT_NAME --tail 5

echo
echo "Логи веб-приложения:"
docker logs $WEBAPP_NAME --tail 5

SERVER_IP=$(hostname -I | awk '{print $1}')

echo
echo "=========================================="
echo "          ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
echo "=========================================="
echo
echo "🌐 Веб-приложение: http://$SERVER_IP"
echo "📡 API сервер: http://$SERVER_IP:8000"
echo "📚 API документация: http://$SERVER_IP/docs"
echo "🤖 Telegram бот: @tvoy_diet_bot"
echo
echo "📊 Для мониторинга используйте:"
echo "docker logs $BOT_NAME -f      # Логи бота"
echo "docker logs $API_NAME -f      # Логи API"
echo "docker logs $WEBAPP_NAME -f   # Логи веб-приложения"
echo
echo "🔄 Для обновления запустите:"
echo "cd $APP_DIR && ./auto-deploy.sh"
echo
echo "⚙️ Конфигурация в файле: $APP_DIR/.env"
echo 