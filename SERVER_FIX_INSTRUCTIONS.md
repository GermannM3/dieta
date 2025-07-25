# 🔧 Исправление проблем на сервере

## ✅ Текущий статус
- **Frontend**: ✅ Работает на порту 5173
- **API**: ✅ Работает на порту 8000
- **Nginx**: ❌ Ошибка конфигурации
- **Бот**: ❌ Не запущен

## 🚨 Проблемы и решения

### 1. Исправление nginx конфигурации

```bash
# Проверка ошибки nginx
sudo nginx -t

# Создание символической ссылки
sudo ln -sf /etc/nginx/sites-available/tvoi-kalkulyator /etc/nginx/sites-enabled/

# Удаление дефолтной конфигурации (если конфликт)
sudo rm -f /etc/nginx/sites-enabled/default

# Перезапуск nginx
sudo systemctl restart nginx
```

### 2. Создание service файлов

```bash
# Копирование service файлов
cp api.service /etc/systemd/system/
cp frontend.service /etc/systemd/system/

# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение и запуск сервисов
sudo systemctl enable --now api frontend nginx
```

### 3. Проверка статуса сервисов

```bash
# Проверка статуса
sudo systemctl status api frontend nginx

# Просмотр логов
sudo journalctl -u api -f
sudo journalctl -u frontend -f
sudo journalctl -u nginx -f
```

### 4. Исправление .env файла

```bash
# Редактирование .env
nano .env
```

**Убедиться, что содержит:**
```env
# ===== YOOKASSA НАСТРОЙКИ =====
YOOKASSA_SHOP_ID=1097156
YOOKASSA_SECRET_KEY=live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA

# ===== API НАСТРОЙКИ =====
API_BASE_URL=http://tvoi-kalkulyator.ru/api
FRONTEND_URL=
```

### 5. Запуск бота

```bash
# Активация окружения
source venv/bin/activate

# Запуск бота в фоне
nohup python main.py > logs/bot.log 2>&1 &
```

## 🔍 Проверка работоспособности

### Локальные тесты
```bash
# API
curl http://localhost:8000/api/health

# Frontend
curl -I http://localhost:5173

# Nginx
curl -I http://localhost
```

### Внешние тесты
```bash
# Через IP
curl -I http://5.129.198.80
curl http://5.129.198.80:8000/api/health

# Через домен (после DNS)
curl -I http://tvoi-kalkulyator.ru
curl http://tvoi-kalkulyator.ru/api/health
```

## 📊 Мониторинг

### Просмотр логов
```bash
# API лог
tail -f logs/api.log

# Frontend лог
tail -f logs/frontend.log

# Бот лог
tail -f logs/bot.log

# Nginx логи
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### Проверка процессов
```bash
# Все процессы
ps aux | grep -E "(python|node|nginx)"

# Порты
netstat -tlnp | grep -E "(8000|5173|80)"
```

## 🎯 Ожидаемый результат

После исправления:
- ✅ `http://tvoi-kalkulyator.ru` → Frontend (React)
- ✅ `http://tvoi-kalkulyator.ru/api/health` → API (FastAPI)
- ✅ Бот отвечает в Telegram
- ✅ Платежи работают с YooKassa 1097156

## 🚨 Если проблемы остаются

### Перезапуск всех сервисов
```bash
# Остановка
sudo systemctl stop api frontend nginx
sudo pkill -f python
sudo pkill -f npm

# Запуск
sudo systemctl start api frontend nginx
nohup python main.py > logs/bot.log 2>&1 &
```

### Проверка конфигурации
```bash
# Nginx
sudo nginx -t
sudo cat /etc/nginx/sites-enabled/tvoi-kalkulyator

# Service файлы
sudo cat /etc/systemd/system/api.service
sudo cat /etc/systemd/system/frontend.service
``` 