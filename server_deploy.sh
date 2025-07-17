#!/bin/bash
echo "🚀 Деплой Диетолог-бота на Timeweb Cloud"
echo "========================================="

# Переходим в правильную папку
echo "📂 Переход в папку /opt/dieta..."
cd /opt/dieta || { echo "❌ Папка /opt/dieta не найдена!"; exit 1; }

# Показываем текущую папку
echo "📍 Текущая папка: $(pwd)"
echo "📋 Содержимое папки:"
ls -la

# Проверяем есть ли проект
if [[ ! -f "main.py" ]]; then
    echo "❌ Проект не найден в /opt/dieta!"
    echo "⬇️ Клонируем проект..."
    
    # Очищаем папку (кроме .env если есть)
    if [[ -f ".env" ]]; then
        cp .env .env.backup
    fi
    
    rm -rf * .*
    
    # Клонируем проект
    git clone https://github.com/GermannM3/dieta.git .
    
    # Восстанавливаем .env
    if [[ -f ".env.backup" ]]; then
        cp .env.backup .env
        rm .env.backup
    fi
fi

# Обновляем проект
echo "🔄 Обновление проекта..."
git pull origin main

# Проверяем и создаем .env файл
if [[ ! -f ".env" ]]; then
    echo "📝 Создание файла .env..."
    cat > .env << 'EOF'
# Telegram Bot
TG_TOKEN=your_telegram_bot_token_here

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://username:password@host:port/database

# AI Services
MISTRAL_API_KEY=your_mistral_key_here
GIGACHAT_CLIENT_SECRET=your_gigachat_secret_here
GIGACHAT_CLIENT_ID=your_gigachat_id_here

# API Configuration
API_BASE_URL=http://5.129.198.80:8000
FRONTEND_URL=http://5.129.198.80:3000

# CalorieNinjas API
CALORIE_NINJAS_API_KEY=your_calorie_ninjas_key_here
EOF
    echo "⚠️ ВАЖНО: Отредактируйте .env файл с реальными ключами!"
    echo "nano .env"
    exit 1
fi

# Проверяем Docker
echo "🐳 Проверка Docker..."
if ! command -v docker &> /dev/null; then
    echo "📥 Установка Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📥 Установка Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Останавливаем старые контейнеры
echo "🛑 Остановка старых контейнеров..."
docker-compose down --remove-orphans 2>/dev/null || true

# Очищаем Docker
echo "🧹 Очистка Docker..."
docker system prune -f

# Запускаем сборку
echo "🔧 Сборка и запуск контейнеров..."
docker-compose up --build -d

# Ждем запуска
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверяем статус
echo "📊 Статус сервисов:"
docker-compose ps

# Проверяем логи
echo "📝 Последние логи:"
docker-compose logs --tail=20

echo ""
echo "✅ Деплой завершен!"
echo ""
echo "🌐 Сервисы доступны по адресам:"
echo "- API: http://5.129.198.80:8000"
echo "- API Docs: http://5.129.198.80:8000/docs"
echo "- Frontend: http://5.129.198.80:3000"
echo ""
echo "📝 Для мониторинга логов: docker-compose logs -f"
echo "🔄 Для перезапуска: docker-compose restart" 