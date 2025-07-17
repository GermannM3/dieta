#!/bin/bash
echo "🔧 Быстрое исправление проблем на сервере Timeweb"
echo "=================================================="

# Переходим в правильную папку
echo "📂 Переход в правильную папку..."
cd /opt/dieta/dieta || { echo "❌ Папка /opt/dieta/dieta не найдена!"; exit 1; }

# Проверяем наличие файлов
echo "📋 Проверяем файлы проекта..."
if [[ ! -f "docker-compose.yml" ]]; then
    echo "❌ docker-compose.yml не найден!"
    echo "⬇️ Скачиваем файлы проекта..."
    curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/docker-compose.yml
    curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/Dockerfile.frontend
fi

# Проверяем и создаем .env файл если нужно
if [[ ! -f ".env" ]]; then
    echo "📝 Создаем файл .env..."
    cat > .env << EOF
# Основные настройки
TG_TOKEN=your_telegram_bot_token_here
DATABASE_URL=postgresql://username:password@host:port/database

# AI сервисы
MISTRAL_API_KEY=your_mistral_key_here
GIGACHAT_CLIENT_SECRET=your_gigachat_secret_here
GIGACHAT_CLIENT_ID=your_gigachat_id_here

# API настройки
API_BASE_URL=http://5.129.198.80:8000
FRONTEND_URL=http://5.129.198.80:3000

# CalorieNinjas API
CALORIE_NINJAS_API_KEY=your_calorie_ninjas_key_here
EOF
    echo "⚠️ ВАЖНО: Отредактируйте .env файл с реальными ключами!"
    echo "nano .env"
fi

# Останавливаем старые контейнеры
echo "🛑 Останавливаем старые контейнеры..."
docker-compose down --remove-orphans

# Очищаем старые образы
echo "🧹 Очищаем старые образы..."
docker system prune -f

# Запускаем сборку и запуск
echo "🚀 Запускаем новую сборку..."
docker-compose up --build -d

# Показываем статус
echo "📊 Статус сервисов:"
docker-compose ps

echo ""
echo "✅ Исправление завершено!"
echo "📝 Если есть ошибки в .env, отредактируйте файл: nano .env"
echo "🔄 Затем перезапустите: docker-compose restart" 