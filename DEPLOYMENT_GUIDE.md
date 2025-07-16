# 🚀 Руководство по деплою веб-приложения "Твой Диетолог"

## 📋 Что сделано

### ✅ Обновления веб-приложения:
1. **🦘 Новая иконка кенгуру** - заменяет сердечко Lovable
2. **📱 Telegram-интеграция** - кликабельная кнопка в правом верхнем углу
3. **🧠 ИИ-диетолог** - подключен к GigaChat API для точного подсчета калорий
4. **🎨 Русификация** - полностью переведен интерфейс
5. **⚙️ Настройка портов** - готов к деплою на порту 3000

### ✅ Telegram-бот кнопка:
- Размещена в правом верхнем углу (fixed position)
- Не навязчивая, стильная
- Ведет на телеграм-бот с текстом "Наш ТГ-бот с ИИ-диетологом"
- Отображается как для зарегистрированных, так и для гостей

### ✅ База данных:
- Подключена Supabase
- Регистрация/авторизация работает
- Сохранение данных о питании

### ✅ ИИ-интеграция:
- Подключен к API на порту 8000 
- Автоматический расчет калорий через GigaChat
- Точная пищевая ценность (белки, жиры, углеводы)

## 🖥️ Структура сервера Timeweb Cloud

### Занятые порты:
- **8000** - API сервер (GigaChat, расчет калорий)
- **8080** - Занят
- **22** - SSH
- **80** - HTTP (nginx)
- **443** - HTTPS (после установки SSL)

### Доступные для веб-приложения:
- **3000** - Наше веб-приложение
- **3001-3999** - Резерв

### Директории:
- `/opt/burassist/` - Telegram-бот (НЕ ТРОГАТЬ!)
- `/opt/diet-webapp/` - Наше веб-приложение
- `/etc/nginx/` - Конфигурация nginx

## 🚀 Деплой веб-приложения

### Вариант 1: Автоматический деплой

**Для Windows:**

PowerShell (рекомендуется):
```powershell
.\deploy-webapp.ps1
```

Batch файл:
```cmd
deploy-webapp.bat
```

**Для Linux/Mac:**
```bash
chmod +x deploy-webapp.sh
./deploy-webapp.sh
```

### Вариант 2: Ручной деплой

#### 1. Подготовка локально:
```bash
cd calorie-love-tracker
npm run build
```

#### 2. Копирование на сервер:
```bash
scp -r dist/* root@5.129.198.80:/opt/diet-webapp/
```

#### 3. На сервере:
```bash
ssh root@5.129.198.80

# Установка Node.js (если нужно)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
apt-get install -y nodejs

# Переход в директорию приложения
cd /opt/diet-webapp

# Установка зависимостей
npm install

# Создание systemd сервиса
cat > /etc/systemd/system/diet-webapp.service << 'EOF'
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
EOF

# Запуск сервиса
systemctl daemon-reload
systemctl enable diet-webapp
systemctl start diet-webapp
```

#### 4. Настройка nginx:
```bash
# Создание конфигурации сайта
cat > /etc/nginx/sites-available/diet-webapp << 'EOF'
server {
    listen 80;
    server_name 5.129.198.80;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Активация сайта
ln -sf /etc/nginx/sites-available/diet-webapp /etc/nginx/sites-enabled/

# Перезагрузка nginx
nginx -t && systemctl reload nginx
```

## 🔒 Установка SSL сертификата

### Бесплатный SSL через Let's Encrypt:
```bash
# Установка certbot
apt update
apt install certbot python3-certbot-nginx

# Получение сертификата (замените example.com на ваш домен)
# Если домена нет, можно использовать IP
certbot --nginx -d 5.129.198.80

# Автоматическое обновление
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

## 🔧 Управление сервисом

### Основные команды:
```bash
# Статус
systemctl status diet-webapp

# Запуск
systemctl start diet-webapp

# Остановка
systemctl stop diet-webapp

# Перезапуск
systemctl restart diet-webapp

# Логи
journalctl -u diet-webapp -f

# Проверка порта
netstat -tulpn | grep :3000
```

## 🌐 Результат

После деплоя веб-приложение будет доступно по адресу:
- **HTTP**: http://5.129.198.80
- **HTTPS** (после SSL): https://5.129.198.80

### 🎯 Функционал:
1. **Регистрация/вход** через Supabase
2. **Трекинг калорий** с ИИ-подсчетом
3. **Telegram-интеграция** через кнопку
4. **Красивый дизайн** с иконкой кенгуру
5. **Адаптивность** под мобильные устройства

## 🔗 Интеграция с Telegram-ботом

### Настройка ссылки на бота:
В файле `.env.production` и в коде укажите правильный username вашего бота:
```
VITE_TELEGRAM_BOT_USERNAME=@your_actual_bot_username
```

### Обновление ссылки:
Замените в `src/pages/Index.tsx`:
```javascript
href="https://t.me/your_actual_bot_username"
```

## 🚨 Важные моменты

1. **НЕ ТРОГАЙТЕ** `/opt/burassist/` - там размещен телеграм-бот
2. **Порты 8000, 8080** заняты - используем **3000**
3. **Nginx** уже настроен - добавляем только наш сайт
4. **API** работает на порту 8000 и уже интегрирован
5. **SSL** рекомендуется установить для безопасности

## ✅ Проверка работы

После деплоя проверьте:
1. Открывается ли сайт по http://5.129.198.80
2. Работает ли регистрация
3. Считаются ли калории через ИИ
4. Переходит ли кнопка на телеграм-бота
5. Сохраняются ли данные в базе

## 📞 Поддержка

При возникновении проблем проверьте:
1. `systemctl status diet-webapp` - статус сервиса
2. `journalctl -u diet-webapp` - логи приложения
3. `nginx -t` - конфигурация nginx
4. `netstat -tulpn | grep :3000` - слушает ли порт

Готово! 🎉 