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

### 3. Диагностика проблем (если нужно)
```bash
python diagnose.py
```

### 4. Исправление зависимостей (если нужно)
```bash
chmod +x fix_dependencies.sh
./fix_dependencies.sh
```

### 5. Запустите все сервисы
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
# Общий лог запуска
tail -f start_all.log

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

## 🚨 Если что-то не работает:

1. **Запустите диагностику**: `python diagnose.py`
2. **Проверьте логи**: `tail -f start_all.log`
3. **Перезапустите**: `python start_all.py`

---

**Всё! Один скрипт запускает всё. 🎉** 