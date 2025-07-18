#!/bin/bash

# Автоматический деплой диетолог-бота на Timeweb Cloud
set -e

echo "🚀 Автоматический деплой 'Твой Диетолог'"
echo "=========================================="

# Конфигурация
REPO_URL="https://github.com/GermannM3/dieta.git"
APP_DIR="/opt/dieta"
COMPOSE_FILE="docker-compose.yml"

# Функция для логирования
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Проверка root прав
if [[ $EUID -ne 0 ]]; then
   echo "❌ Этот скрипт должен запускаться от root" 
    exit 1
fi

log "📦 Обновление системы..."
apt update && apt upgrade -y

log "🐳 Установка Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

log "🔧 Установка Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

log "📂 Подготовка директории приложения..."
mkdir -p $APP_DIR
    cd $APP_DIR

# Остановка существующих контейнеров
log "🛑 Остановка существующих сервисов..."
if [ -f $COMPOSE_FILE ]; then
    docker-compose down || true
fi

# Клонирование/обновление репозитория
if [ -d ".git" ]; then
    log "🔄 Обновление кода из GitHub..."
    git fetch origin
    git reset --hard origin/main
    git clean -fd
else
    log "⬇️ Клонирование репозитория..."
    rm -rf * .*
    git clone $REPO_URL .
fi

# Проверка файла окружения
if [ ! -f ".env" ]; then
    log "⚠️ Файл .env не найден!"
    log "📝 Создание шаблона .env..."
    cp env.example .env
    
    echo "❌ КРИТИЧНО: Необходимо настроить файл .env!"
    echo "📋 Отредактируйте файл: nano $APP_DIR/.env"
    echo "🔑 Заполните:"
    echo "   - TG_TOKEN (токен Telegram бота)"
    echo "   - DATABASE_URL (подключение к PostgreSQL)"
    echo "   - MISTRAL_API_KEY (ключ Mistral AI)"
    echo "   - GIGACHAT_* (ключи GigaChat)"
    echo ""
    echo "⚡ После настройки запустите: $APP_DIR/auto-deploy.sh"
    exit 1
fi

log "🔍 Проверка файла .env..."
source .env

# Проверка обязательных переменных
required_vars=("TG_TOKEN" "DATABASE_URL" "MISTRAL_API_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Переменная $var не установлена в .env"
        exit 1
    fi
done

log "✅ Конфигурация корректна"

# Сборка и запуск контейнеров
log "🏗️ Сборка и запуск сервисов..."
docker-compose up --build -d

# Ожидание запуска сервисов
log "⏳ Ожидание запуска сервисов..."
sleep 30

# Проверка статуса
log "📊 Проверка статуса сервисов..."
docker-compose ps

# Проверка логов
log "📝 Последние логи API сервера:"
docker-compose logs --tail=10 api

log "📝 Последние логи Telegram бота:"
docker-compose logs --tail=10 bot

log "📝 Последние логи веб-приложения:"
docker-compose logs --tail=10 frontend

# Проверка доступности
log "🌐 Проверка доступности сервисов..."

# API сервер
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log "✅ API сервер работает"
else
    log "⚠️ API сервер недоступен"
fi

# Веб-приложение
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    log "✅ Веб-приложение работает"
else
    log "⚠️ Веб-приложение недоступен"
fi

# Настройка nginx (если не настроен)
if [ ! -f "/etc/nginx/sites-available/dieta" ]; then
    log "🔧 Настройка Nginx..."
    
    # Установка nginx
    apt install -y nginx
    
    # Создание конфигурации
    cat > /etc/nginx/sites-available/dieta << 'NGINX_EOF'
server {
    listen 80;
    server_name _;
    
    # Веб-приложение (главная страница)
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API сервер
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Документация API
    location /docs {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_EOF

    # Активация сайта
    ln -sf /etc/nginx/sites-available/dieta /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
    
    # Перезапуск nginx
    nginx -t && systemctl restart nginx
    systemctl enable nginx
    
    log "✅ Nginx настроен"
fi

echo ""
echo "🎉 ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
echo "================================"
echo "🌐 Веб-приложение: http://$(curl -s ifconfig.me)"
echo "🔗 API документация: http://$(curl -s ifconfig.me)/docs"
echo "🤖 Telegram бот: @tvoy_diet_bot"
echo ""
echo "📊 Управление сервисами:"
echo "   Статус:     docker-compose ps"
echo "   Логи:       docker-compose logs -f [api|bot|frontend]"
echo "   Перезапуск: docker-compose restart [api|bot|frontend]"
echo "   Остановка:  docker-compose down"
echo ""
echo "🔄 Для обновления запустите: $APP_DIR/auto-deploy.sh" 