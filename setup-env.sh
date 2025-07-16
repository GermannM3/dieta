#!/bin/bash

# Быстрая настройка переменных окружения для Твой Диетолог
# Используйте этот скрипт ПЕРЕД запуском auto-deploy.sh

echo "⚙️ Настройка переменных окружения для Твой Диетолог"
echo "=================================================="
echo

APP_DIR="/opt/dieta"
ENV_FILE="$APP_DIR/.env"

# Создаем директорию если её нет
mkdir -p $APP_DIR

echo "🔑 Введите ваши данные:"
echo

# Telegram Bot данные
read -p "Введите токен Telegram бота (от @BotFather): " TG_TOKEN
read -p "Введите ваш Telegram ID (admin): " ADMIN_ID

echo
echo "🗄️ База данных:"
read -p "Введите DATABASE_URL (PostgreSQL): " DATABASE_URL

echo
echo "🤖 API ключи:"
read -p "GigaChat Client ID: " GIGACHAT_CLIENT_ID
read -p "GigaChat Auth Key: " GIGACHAT_AUTH_KEY
read -p "GigaChat Access Token: " GIGACHAT_ACCESS_TOKEN
read -p "Mistral API Key: " MISTRAL_API_KEY
read -p "CalorieNinjas API Key: " CALORIE_NINJAS_API_KEY

echo
echo "💾 Создание .env файла..."

# Создаем .env файл
cat > $ENV_FILE << EOF
# Telegram Bot Configuration
TG_TOKEN=$TG_TOKEN
ADMIN_ID=$ADMIN_ID

# Database Configuration
DATABASE_URL=$DATABASE_URL

# AI API Keys
GIGACHAT_CLIENT_ID=$GIGACHAT_CLIENT_ID
GIGACHAT_AUTH_KEY=$GIGACHAT_AUTH_KEY
GIGACHAT_ACCESS_TOKEN=$GIGACHAT_ACCESS_TOKEN
MISTRAL_API_KEY=$MISTRAL_API_KEY
CALORIE_NINJAS_API_KEY=$CALORIE_NINJAS_API_KEY

# Optional Settings
LOG_LEVEL=INFO
API_PORT=8000
EOF

echo "✅ Файл $ENV_FILE создан успешно!"
echo
echo "🚀 Теперь запустите деплой:"
echo "curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/auto-deploy.sh"
echo "chmod +x auto-deploy.sh"
echo "./auto-deploy.sh"
echo 