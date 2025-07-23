# 🚀 Простой запуск Dieta Bot

## 📋 Что нужно сделать на сервере:

### 1. Подключитесь к серверу
```bash
ssh root@5.129.198.80
cd /opt/dieta
```

### 2. Активируйте виртуальное окружение
```bash
source venv/bin/activate
```

### 3. Установите зависимости (если нужно)
```bash
pip install -r requirements.txt
```

### 4. Запустите все сервисы
```bash
python start_all.py
```

## 🌐 После запуска будет доступно:

- **Веб-сайт**: http://tvoi-kalkulyator.ru
- **Альтернативный домен**: http://твой-калькулятор.рф
- **API**: http://tvoi-kalkulyator.ru/api/health
- **Telegram бот**: @tvoy_diet_bot

## 🛑 Остановка:

Нажмите `Ctrl+C` в терминале где запущен скрипт.

## 📊 Логи:

```bash
# API
tail -f logs/api.log

# Фронтенд
tail -f logs/frontend.log

# Бот
tail -f logs/bot.log

# Nginx
tail -f /var/log/nginx/tvoi-kalkulyator.error.log
```

## 🔍 Проверка:

```bash
# API
curl http://localhost:8000/health

# Фронтенд
curl -I http://localhost:3000

# Сайт
curl -I http://tvoi-kalkulyator.ru
```

---

**Всё! Один скрипт запускает всё. 🎉** 