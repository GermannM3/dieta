# 🔥 Быстрое исправление сервера

## 🚨 Текущие проблемы:
- **API**: порт 8000 занят
- **Nginx**: порт 80 занят  
- **Bot**: две копии (TelegramConflictError)

## ✅ Пошаговое исправление:

### 1. Остановить все процессы
```bash
# Остановка systemd сервисов
sudo systemctl stop api frontend nginx

# Убить все процессы Python и nginx
sudo pkill -f "python.*improved_api_server"
sudo pkill -f "python.*main"
sudo pkill -f "nginx"
sudo pkill -f "npm"

# Проверить что порты свободны
netstat -tlnp | grep -E "(8000|80|5173)"
```

### 2. Очистить порты
```bash
# Принудительно освободить порты
sudo lsof -ti :8000 | xargs sudo kill -9
sudo lsof -ti :80 | xargs sudo kill -9
sudo lsof -ti :5173 | xargs sudo kill -9
```

### 3. Перезапустить сервисы
```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Запуск сервисов
sudo systemctl start api frontend nginx

# Проверка статуса
sudo systemctl status api frontend nginx
```

### 4. Запустить бота (только одну копию)
```bash
# Убить все процессы бота
sudo pkill -f "python.*main"

# Запустить одну копию
source venv/bin/activate
nohup python main.py > logs/bot.log 2>&1 &

# Проверить что только один процесс
ps aux | grep "python.*main"
```

## 🔍 Проверка работоспособности

### Локальные тесты
```bash
# API
curl -I http://localhost:8000/api/health

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
curl -I http://5.129.198.80:5173

# Через домен (после DNS)
curl -I http://tvoi-kalkulyator.ru
curl http://tvoi-kalkulyator.ru/api/health
```

## 📊 Мониторинг

### Проверка процессов
```bash
# Все процессы
ps aux | grep -E "(python|node|nginx)"

# Порты
netstat -tlnp | grep -E "(8000|5173|80)"
```

### Просмотр логов
```bash
# API
sudo journalctl -u api -f

# Frontend
sudo journalctl -u frontend -f

# Nginx
sudo journalctl -u nginx -f

# Bot
tail -f logs/bot.log
```

## 🎯 Ожидаемый результат

После исправления:
- ✅ **API**: `http://5.129.198.80:8000/api/health` → 200 OK
- ✅ **Frontend**: `http://5.129.198.80:5173` → 200 OK  
- ✅ **Nginx**: `http://5.129.198.80` → 200 OK
- ✅ **Bot**: один процесс, без конфликтов

## 🚨 Если проблемы остаются

### Полная перезагрузка
```bash
# Остановить все
sudo systemctl stop api frontend nginx
sudo pkill -f python
sudo pkill -f npm
sudo pkill -f nginx

# Подождать
sleep 5

# Запустить заново
sudo systemctl start api frontend nginx
source venv/bin/activate
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

# 🚨 БЫСТРОЕ ИСПРАВЛЕНИЕ REDIS ОШИБКИ

## 1. Убить лишний процесс бота
```bash
sudo pkill -f "python main.py"
ps aux | grep 'main.py' | grep -v grep
# Должна быть ТОЛЬКО ОДНА строка!
```

## 2. Перезапустить бота
```bash
sudo systemctl restart bot
sudo systemctl status bot
```

## 3. Проверить логи
```bash
sudo journalctl -u bot -f
```

## 4. Протестировать в Telegram
```
/start
```

## ✅ Ожидаемый результат:
- Нет ошибок Redis
- Бот отвечает на команды
- Один процесс бота
- Все функции работают 