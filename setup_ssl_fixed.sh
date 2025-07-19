#!/bin/bash

echo "🔒 Настройка SSL сертификатов для доменов"
echo "=========================================="

# 1. Установка Certbot
echo "📦 Установка Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. Создаем временный Nginx конфиг только для HTTP
echo "📝 Создание временного Nginx конфига..."
sudo tee /etc/nginx/sites-available/temp-ssl.conf >/dev/null <<'EOF'
# Временный конфиг для получения сертификатов
server {
    listen 80;
    server_name tvoi-kalkulyator.ru www.tvoi-kalkulyator.ru твой-калькулятор.рф www.твой-калькулятор.рф;
    
    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 3. Включаем временный конфиг
sudo ln -sf /etc/nginx/sites-available/temp-ssl.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 4. Получение SSL сертификатов
echo "🔐 Получение SSL сертификатов..."
echo "⚠️  Убедитесь, что домены указывают на этот сервер (5.129.198.80)"
echo "⚠️  Если используете Cloudflare, временно отключите прокси (серое облако)"

sudo certbot --nginx -d tvoi-kalkulyator.ru -d www.tvoi-kalkulyator.ru -d твой-калькулятор.рф -d www.твой-калькулятор.рф

# 5. Удаляем временный конфиг
sudo rm /etc/nginx/sites-enabled/temp-ssl.conf

# 6. Копируем финальный SSL конфиг
echo "📝 Настройка финального SSL конфига..."
sudo cp ssl-domains.conf /etc/nginx/sites-available/ssl-domains.conf
sudo ln -sf /etc/nginx/sites-available/ssl-domains.conf /etc/nginx/sites-enabled/

# 7. Проверка и перезагрузка
echo "🔍 Проверка конфигурации Nginx..."
sudo nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Nginx конфигурация корректна"
    sudo systemctl reload nginx
else
    echo "❌ Ошибка в конфигурации Nginx"
    exit 1
fi

echo "✅ SSL настройка завершена!"
echo "🌐 Проверьте сайты:"
echo "   https://tvoi-kalkulyator.ru"
echo "   https://твой-калькулятор.рф" 