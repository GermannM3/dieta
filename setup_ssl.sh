#!/bin/bash

echo "🔒 Настройка SSL сертификатов для доменов"
echo "=========================================="

# 1. Установка Certbot
echo "📦 Установка Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# 2. Копирование Nginx конфига
echo "📝 Настройка Nginx..."
sudo cp ssl-domains.conf /etc/nginx/sites-available/ssl-domains.conf
sudo ln -sf /etc/nginx/sites-available/ssl-domains.conf /etc/nginx/sites-enabled/

# 3. Проверка Nginx конфига
echo "🔍 Проверка конфигурации Nginx..."
sudo nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Nginx конфигурация корректна"
    sudo systemctl reload nginx
else
    echo "❌ Ошибка в конфигурации Nginx"
    exit 1
fi

# 4. Получение SSL сертификатов
echo "🔐 Получение SSL сертификатов..."
echo "⚠️  Убедитесь, что домены указывают на этот сервер (5.129.198.80)"
echo "⚠️  Если используете Cloudflare, временно отключите прокси (оранжевое облако)"
echo ""
read -p "Продолжить? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Отменено"
    exit 1
fi

# Получаем сертификаты
sudo certbot --nginx \
    -d tvoi-kalkulyator.ru \
    -d www.tvoi-kalkulyator.ru \
    -d твой-калькулятор.рф \
    -d www.твой-калькулятор.рф \
    --non-interactive \
    --agree-tos \
    --email germannm@vk.com \
    --redirect

# 5. Проверка статуса
echo "📊 Проверка статуса сертификатов..."
sudo certbot certificates

# 6. Настройка автообновления
echo "🔄 Настройка автообновления..."
sudo systemctl status certbot.timer

# 7. Финальная проверка
echo "✅ SSL настройка завершена!"
echo "🌐 Проверьте сайты:"
echo "   - https://tvoi-kalkulyator.ru"
echo "   - https://твой-калькулятор.рф" 