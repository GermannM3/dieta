# 🚀 Инструкция по деплою на сервер

## 📋 Git Workflow

### 1. Подготовка к деплою
```bash
# Проверка статуса
git status

# Добавление всех изменений
git add .

# Коммит изменений
git commit -m "Обновление конфигурации для продакшена: YooKassa 1097156, порт 5173, домен tvoi-kalkulyator.ru"

# Пуш в репозиторий
git push origin main
```

### 2. Подключение к серверу
```bash
ssh root@5.129.198.80
# Пароль: z.BqR?PLrJ8QZ8
```

### 3. Обновление кода на сервере
```bash
# Переход в директорию проекта
cd /opt/dieta

# Создание резервной копии
cp .env .env.backup

# Пул последних изменений
git pull origin main

# Активация виртуального окружения
source venv/bin/activate
```

## 🔧 Обновление конфигурации на сервере

### 1. Обновление .env файла
```bash
# Редактирование .env файла
nano .env
```

**Добавить/обновить строки:**
```env
# ===== YOOKASSA НАСТРОЙКИ =====
YOOKASSA_SHOP_ID=1097156
YOOKASSA_SECRET_KEY=live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA
```

### 2. Обновление nginx конфигурации
```bash
# Копирование обновленной конфигурации
cp nginx-prod.conf /etc/nginx/sites-available/tvoi-kalkulyator

# Создание символической ссылки (если не существует)
ln -sf /etc/nginx/sites-available/tvoi-kalkulyator /etc/nginx/sites-enabled/

# Проверка конфигурации
sudo nginx -t

# Перезапуск nginx
sudo systemctl restart nginx
```

### 3. Обновление frontend.service
```bash
# Копирование service файла
cp frontend.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение и запуск frontend сервиса
sudo systemctl enable --now frontend
```

### 4. Обновление frontend .env
```bash
# Проверка .env файла frontend
cat /opt/dieta/calorie-love-tracker/.env
```

**Должен содержать:**
```env
VITE_API_URL=http://tvoi-kalkulyator.ru/api
VITE_APP_TITLE=Твой Диетолог - Персональный ИИ-помощник
VITE_APP_DESCRIPTION=Продвинутый телеграм-бот с личным диетологом
VITE_TELEGRAM_BOT_USERNAME=@tvoy_diet_bot
PORT=5173
```

## 🚀 Запуск всех сервисов

### 1. Остановка предыдущих процессов
```bash
# Остановка всех сервисов
python stop_all.py
```

### 2. Запуск всех сервисов
```bash
# Запуск всех сервисов одним файлом
python start_all_services.py
```

### 3. Альтернативный запуск (если нужно)
```bash
# Запуск в фоновом режиме
nohup python start_all.py > start_all.log 2>&1 &
```

## 🔍 Проверка работоспособности

### 1. Проверка API
```bash
# Локально на сервере
curl http://localhost:8000/health

# Через домен
curl http://tvoi-kalkulyator.ru/api/health
```

### 2. Проверка frontend
```bash
# Локально на сервере
curl -I http://localhost:5173

# Через домен
curl -I http://tvoi-kalkulyator.ru
```

### 3. Проверка бота
```bash
# Проверка логов бота
tail -f logs/bot.log
```

### 4. Проверка платежей
```bash
# Тест создания платежа
python test_premium.py
```

## 📊 Мониторинг

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
- ✅ Frontend работает на порту 5173

---

**В случае проблем обращайтесь к логам и используйте команды диагностики!** 