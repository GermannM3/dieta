#!/bin/bash

echo "🔧 Очистка и настройка SSL с нуля"
echo "================================="

# 1. Очищаем все старые SSL конфиги
echo "🧹 Очистка старых SSL конфигов..."
sudo rm -f /etc/nginx/sites-enabled/ssl-domains.conf
sudo rm -f /etc/nginx/sites-enabled/temp-ssl.conf
sudo rm -f /etc/nginx/sites-available/ssl-domains.conf
sudo rm -f /etc/nginx/sites-available/temp-ssl.conf

# 2. Проверяем что Nginx работает
echo "🔍 Проверка Nginx..."
sudo nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx конфигурация сломана, исправляем..."
    sudo rm -f /etc/nginx/sites-enabled/*
    sudo nginx -t
fi

# 3. Создаем простой HTTP конфиг для получения сертификатов
echo "📝 Создание простого HTTP конфига..."
sudo tee /etc/nginx/sites-available/certbot.conf >/dev/null <<'EOF'
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

# 4. Включаем конфиг
sudo ln -sf /etc/nginx/sites-available/certbot.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 5. Получаем сертификаты для латинского домена
echo "🔐 Получение сертификатов для tvoi-kalkulyator.ru..."
sudo certbot --nginx -d tvoi-kalkulyator.ru -d www.tvoi-kalkulyator.ru --non-interactive --agree-tos --email germannm@vk.com --redirect

# 6. Получаем сертификаты для кириллического домена (punycode)
echo "🔐 Получение сертификатов для кириллического домена..."
CYRILLIC_DOMAIN="твой-калькулятор.рф"
PUNYCODE_DOMAIN=$(python3 -c "
import sys
sys.path.append('/usr/lib/python3/dist-packages')
import idna
print(idna.encode('$CYRILLIC_DOMAIN').decode('ascii'))
")

echo "🔗 Punycode домен: $PUNYCODE_DOMAIN"
sudo certbot --nginx -d "$PUNYCODE_DOMAIN" -d "www.$PUNYCODE_DOMAIN" --non-interactive --agree-tos --email germannm@vk.com --redirect

# 7. Проверяем что сертификаты получены
echo "✅ Проверка полученных сертификатов..."
sudo certbot certificates

echo "✅ SSL настройка завершена!"
echo "🌐 Проверьте сайты:"
echo "   https://tvoi-kalkulyator.ru"
echo "   https://твой-калькулятор.рф" 