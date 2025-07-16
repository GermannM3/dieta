#!/bin/bash

# Скрипт деплоя веб-приложения "Твой Диетолог" на Timeweb Cloud

set -e

echo "🚀 Начинаю деплой веб-приложения 'Твой Диетолог'..."

# Переменные
SERVER_IP="5.129.198.80"
SERVER_USER="root"
APP_NAME="diet-webapp"
LOCAL_APP_DIR="./calorie-love-tracker"
REMOTE_APP_DIR="/opt/diet-webapp"
REMOTE_DEPLOY_DIR="/opt/deploy"

echo "📦 Создаем архив приложения..."
tar -czf diet-webapp.tar.gz -C calorie-love-tracker .

echo "📤 Копируем файлы на сервер..."
scp diet-webapp.tar.gz ${SERVER_USER}@${SERVER_IP}:/tmp/

echo "🔧 Подключаемся к серверу и развертываем..."
ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
    # Создаем директории
    mkdir -p /opt/diet-webapp
    mkdir -p /opt/deploy/diet-webapp
    
    # Очищаем предыдущую версию
    rm -rf /opt/diet-webapp/*
    
    # Распаковываем новую версию
    cd /opt/diet-webapp
    tar -xzf /tmp/diet-webapp.tar.gz
    
    # Устанавливаем Node.js и npm если не установлены
    if ! command -v node &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        apt-get install -y nodejs
    fi
    
    # Устанавливаем зависимости
    npm install
    
    # Собираем приложение для продакшна
    npm run build
    
    # Создаем systemd сервис
    cat > /etc/systemd/system/diet-webapp.service << SYSTEMD_EOF
[Unit]
Description=Diet WebApp
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/diet-webapp
ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0 --port 3000
Restart=always
Environment=NODE_ENV=production
Environment=PORT=3000

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF
    
    # Перезагружаем systemd и запускаем сервис
    systemctl daemon-reload
    systemctl enable diet-webapp
    systemctl restart diet-webapp
    
    # Проверяем статус
    sleep 5
    systemctl status diet-webapp
    
    # Обновляем конфигурацию nginx для проксирования
    cat > /etc/nginx/sites-available/diet-webapp << NGINX_EOF
server {
    listen 80;
    server_name 5.129.198.80;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX_EOF
    
    # Активируем сайт
    ln -sf /etc/nginx/sites-available/diet-webapp /etc/nginx/sites-enabled/
    
    # Тестируем и перезагружаем nginx
    nginx -t && systemctl reload nginx
    
    # Очищаем временные файлы
    rm -f /tmp/diet-webapp.tar.gz
    
    echo "✅ Деплой завершен!"
    echo "🌐 Веб-приложение доступно по адресу: http://5.129.198.80"
    echo "📊 Статус сервиса:"
    systemctl status diet-webapp --no-pager -l
EOF

# Очищаем локальные временные файлы
rm -f diet-webapp.tar.gz

echo "🎉 Деплой успешно завершен!"
echo "🌐 Ваше веб-приложение доступно по адресу: http://5.129.198.80" 