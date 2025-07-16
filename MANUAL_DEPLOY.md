# 🚀 Ручной деплой веб-приложения

## Проблема
Автоматические скрипты требуют настройки SSH ключей. Для быстрого деплоя выполните команды вручную.

## 📋 Пошаговая инструкция

### Шаг 1: Подключение к серверу
```bash
ssh root@5.129.198.80
# Пароль: z.BqR?PLrJ8QZ8
```

### Шаг 2: Остановка старого контейнера (если есть)
```bash
docker stop diet-webapp 2>/dev/null || true
docker rm diet-webapp 2>/dev/null || true
```

### Шаг 3: Создание директории
```bash
mkdir -p /opt/diet-webapp
cd /opt/diet-webapp
```

### Шаг 4: Загрузка файлов
Вариант A: Через Git (если есть репозиторий)
```bash
git clone <your-repo-url> .
cd calorie-love-tracker
```

Вариант B: Ручная загрузка
- Заархивируйте папку `calorie-love-tracker`
- Загрузите через SCP или панель управления хостинга
- Распакуйте в `/opt/diet-webapp/`

### Шаг 5: Сборка Docker образа
```bash
cd /opt/diet-webapp
docker build -t diet-webapp:latest \
  --build-arg VITE_API_URL=http://5.129.198.80:8000 \
  --build-arg VITE_APP_TITLE="Твой Диетолог - Персональный ИИ-помощник" \
  --build-arg VITE_APP_DESCRIPTION="Продвинутый телеграм-бот с личным диетологом" \
  --build-arg VITE_TELEGRAM_BOT_USERNAME=@tvoy_diet_bot \
  .
```

### Шаг 6: Запуск контейнера
```bash
docker run -d \
  --name diet-webapp \
  --restart unless-stopped \
  -p 3000:3000 \
  diet-webapp:latest
```

### Шаг 7: Настройка nginx
```bash
cat > /etc/nginx/sites-available/webapp << 'EOL'
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
EOL

ln -sf /etc/nginx/sites-available/webapp /etc/nginx/sites-enabled/webapp
nginx -t && systemctl reload nginx
```

### Шаг 8: Проверка
```bash
# Проверить контейнер
docker ps | grep diet-webapp

# Проверить логи
docker logs diet-webapp

# Проверить nginx
curl -I localhost:3000
```

## ✅ Результат

После выполнения всех шагов веб-приложение будет доступно по адресу:
**http://5.129.198.80**

## 🔧 Устранение проблем

### Если контейнер не запускается:
```bash
docker logs diet-webapp
```

### Если nginx не работает:
```bash
nginx -t
systemctl status nginx
```

### Если порт 3000 занят:
```bash
netstat -tulpn | grep :3000
```

## 🚨 Важно

- НЕ трогайте `/opt/burassist/` - там Telegram-бот!
- Порт 8000 уже занят API сервером
- После деплоя кнопка в веб-приложении будет вести на @tvoy_diet_bot

## 📱 Альтернатива - деплой через Timeweb Apps

Можно также использовать встроенный сервис Apps в панели Timeweb Cloud:
1. Подключите Git репозиторий
2. Выберите папку `calorie-love-tracker`
3. Укажите команду сборки: `npm run build`
4. Укажите команду запуска: `npm run preview`
5. Задайте переменные окружения из `.env.production` 