#!/bin/bash

echo "🔒 Настройка SSL сертификатов для доменов (включая кириллический)"
echo "================================================================"

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
    server_name tvoi-kalkulyator.ru www.tvoi-kalkulyator.ru;
    
    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Отдельный сервер для кириллического домена
server {
    listen 80;
    server_name твой-калькулятор.рф www.твой-калькулятор.рф;
    
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

# 4. Получение SSL сертификатов для латинского домена
echo "🔐 Получение SSL сертификатов для tvoi-kalkulyator.ru..."
echo "⚠️  Убедитесь, что домены указывают на этот сервер (5.129.198.80)"
echo "⚠️  Если используете Cloudflare, временно отключите прокси (серое облако)"

sudo certbot --nginx -d tvoi-kalkulyator.ru -d www.tvoi-kalkulyator.ru

# 5. Получение SSL сертификатов для кириллического домена (используем punycode)
echo "🔐 Получение SSL сертификатов для кириллического домена..."
echo "📝 Конвертируем кириллический домен в punycode..."

# Конвертируем кириллический домен в punycode
CYRILLIC_DOMAIN="твой-калькулятор.рф"
PUNYCODE_DOMAIN=$(python3 -c "
import sys
sys.path.append('/usr/lib/python3/dist-packages')
import idna
print(idna.encode('$CYRILLIC_DOMAIN').decode('ascii'))
")

echo "🔗 Кириллический домен: $CYRILLIC_DOMAIN"
echo "🔗 Punycode домен: $PUNYCODE_DOMAIN"

# Получаем сертификат для punycode домена
sudo certbot --nginx -d "$PUNYCODE_DOMAIN" -d "www.$PUNYCODE_DOMAIN"

# 6. Удаляем временный конфиг
sudo rm /etc/nginx/sites-enabled/temp-ssl.conf

# 7. Создаем финальный SSL конфиг с правильными путями
echo "📝 Создание финального SSL конфига..."
sudo tee /etc/nginx/sites-available/ssl-domains.conf >/dev/null <<EOF
# tvoi-kalkulyator.ru
server {
    listen 80;
    server_name tvoi-kalkulyator.ru www.tvoi-kalkulyator.ru;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tvoi-kalkulyator.ru www.tvoi-kalkulyator.ru;

    ssl_certificate     /etc/letsencrypt/live/tvoi-kalkulyator.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tvoi-kalkulyator.ru/privkey.pem;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

# твой-калькулятор.рф (кириллический)
server {
    listen 80;
    server_name твой-калькулятор.рф www.твой-калькулятор.рф;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name твой-калькулятор.рф www.твой-калькулятор.рф;

    ssl_certificate     /etc/letsencrypt/live/$PUNYCODE_DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$PUNYCODE_DOMAIN/privkey.pem;

    # SSL настройки
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# 8. Включаем финальный конфиг
sudo ln -sf /etc/nginx/sites-available/ssl-domains.conf /etc/nginx/sites-enabled/

# 9. Проверка и перезагрузка
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