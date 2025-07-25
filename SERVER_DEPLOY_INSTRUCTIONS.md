# 🚀 Инструкция по деплою на сервер

## 📋 Предварительные требования

### 1. Подключение к серверу
```bash
ssh root@5.129.198.80
# Пароль: z.BqR?PLrJ8QZ8
```

### 2. Проверка системы
```bash
# Проверка версий
python3 --version
node --version
npm --version
nginx -v

# Проверка статуса сервисов
sudo systemctl status nginx
sudo systemctl status frontend
```

## 🔧 Шаг 1: Обновление файлов на сервере

### Копирование обновленных файлов
```bash
# Создание резервной копии
cd /opt/dieta
cp .env .env.backup

# Обновление .env файла (внести изменения вручную)
nano .env
```

### Необходимые изменения в .env:
```diff
# ===== YOOKASSA НАСТРОЙКИ =====
- YOOKASSA_SHOP_ID=381764678
- YOOKASSA_SECRET_KEY=TEST:132209
+ YOOKASSA_SHOP_ID=1097156
+ YOOKASSA_SECRET_KEY=live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA
```

### Обновление nginx конфигурации
```bash
# Редактирование конфигурации
sudo nano /etc/nginx/sites-enabled/tvoi-kalkulyator
```

### Содержимое nginx конфигурации:
```nginx
server {
    listen 80;
    server_name tvoi-kalkulyator.ru;

    location / {
        proxy_pass http://127.0.0.1:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Обновление frontend.service
```bash
# Копирование нового service файла
sudo cp frontend.service /etc/systemd/system/
```

## 🔧 Шаг 2: Обновление frontend .env

```bash
# Редактирование .env файла frontend
nano /opt/dieta/calorie-love-tracker/.env
```

### Содержимое .env:
```env
VITE_API_URL=http://tvoi-kalkulyator.ru/api
VITE_APP_TITLE=Твой Диетолог - Персональный ИИ-помощник
VITE_APP_DESCRIPTION=Продвинутый телеграм-бот с личным диетологом
VITE_TELEGRAM_BOT_USERNAME=@tvoy_diet_bot
PORT=5173
```

## 🔧 Шаг 3: Перезапуск сервисов

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение и запуск frontend сервиса
sudo systemctl enable --now frontend

# Перезапуск nginx
sudo systemctl restart nginx

# Проверка статуса
sudo systemctl status frontend
sudo systemctl status nginx
```

## 🚀 Шаг 4: Запуск всех сервисов

### Активация окружения
```bash
cd /opt/dieta
source venv/bin/activate
```

### Запуск всех сервисов одним файлом
```bash
# Остановка предыдущих процессов (если есть)
python stop_all.py

# Запуск всех сервисов
python start_all_services.py
```

### Альтернативный запуск (если start_all_services.py не работает)
```bash
# Запуск в фоновом режиме
nohup python start_all.py > start_all.log 2>&1 &
```

## 🔍 Шаг 5: Проверка работоспособности

### Проверка API
```bash
# Локально на сервере
curl http://localhost:8000/health

# Через домен
curl http://tvoi-kalkulyator.ru/api/health
```

### Проверка frontend
```bash
# Локально на сервере
curl -I http://localhost:5173

# Через домен
curl -I http://tvoi-kalkulyator.ru
```

### Проверка бота
```bash
# Проверка логов бота
tail -f logs/bot.log
```

### Проверка платежей
```bash
# Тест создания платежа
python test_premium.py
```

## 📊 Мониторинг и логи

### Просмотр логов
```bash
# Общий лог
tail -f start_all.log

# Отдельные логи
tail -f logs/api.log
tail -f logs/frontend.log
tail -f logs/bot.log

# Nginx логи
tail -f /var/log/nginx/tvoi-kalkulyator.error.log
tail -f /var/log/nginx/tvoi-kalkulyator.access.log
```

### Проверка процессов
```bash
# Проверка запущенных процессов
ps aux | grep python
ps aux | grep node
ps aux | grep nginx

# Проверка портов
netstat -tlnp | grep :8000
netstat -tlnp | grep :5173
netstat -tlnp | grep :80
```

## 🛠 Устранение проблем

### Если frontend не запускается
```bash
# Проверка npm
cd /opt/dieta/calorie-love-tracker
npm install
npm start

# Проверка логов
sudo journalctl -u frontend -f
```

### Если API не отвечает
```bash
# Проверка зависимостей
pip install -r requirements.txt

# Ручной запуск API
python api_server.py
```

### Если nginx не работает
```bash
# Проверка конфигурации
sudo nginx -t

# Перезапуск
sudo systemctl restart nginx
```

### Если бот не отвечает
```bash
# Проверка токена
echo $TG_TOKEN

# Ручной запуск бота
python main.py
```

## ✅ Финальная проверка

### 1. Проверка сайта
- Откройте `http://tvoi-kalkulyator.ru`
- Должна загрузиться главная страница

### 2. Проверка API
- Откройте `http://tvoi-kalkulyator.ru/api/health`
- Должен вернуться статус "OK"

### 3. Проверка бота
- Напишите боту `@tvoy_diet_bot`
- Должен ответить приветствием

### 4. Проверка платежей
- Попробуйте создать тестовый платеж
- Должен создаться с чеком для самозанятых

## 🎉 Готово!

После выполнения всех шагов:
- ✅ Сайт доступен по адресу `tvoi-kalkulyator.ru`
- ✅ API работает на `tvoi-kalkulyator.ru/api`
- ✅ Бот работает с магазином `1097156`
- ✅ Платежи создают чеки с `vat_code:1`
- ✅ Возврат после оплаты идет в Telegram

---

**В случае проблем обращайтесь к логам и используйте команды диагностики!** 