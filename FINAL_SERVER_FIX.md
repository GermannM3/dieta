# 🚀 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ - Dieta Bot

## ❌ Проблемы, которые были исправлены:

1. **Неправильные порты** - сайт должен работать на порту 80, а не 3000
2. **Неправильные домены** - настроены домены `tvoi-kalkulyator.ru` и `твой-калькулятор.рф`
3. **Конфликт зависимостей** - исправлен конфликт между `aiogram`, `fastapi` и `mistralai`
4. **Неправильная конфигурация nginx** - создана правильная конфигурация для доменов

## 🔧 Быстрое исправление на сервере:

### 1. Подключитесь к серверу
```bash
ssh root@5.129.198.80
cd /opt/dieta
```

### 2. Остановите все процессы
```bash
pkill -f "main.py" || true
pkill -f "improved_api_server.py" || true
pkill -f "npm start" || true
pkill -f "nginx" || true
```

### 3. Активируйте виртуальное окружение
```bash
source venv/bin/activate
```

### 4. Исправьте зависимости
```bash
chmod +x fix_dependencies.sh
./fix_dependencies.sh
```

### 5. Запустите все сервисы
```bash
chmod +x fix_and_start.sh
./fix_and_start.sh
```

## 🌐 Правильная архитектура:

```
Интернет → Nginx (порт 80) → Frontend (порт 3000)
                    ↓
                API (порт 8000)
                    ↓
                Telegram Bot
```

## 📋 Проверка работы:

### 1. Проверьте API
```bash
curl http://localhost:8000/health
# Должен вернуть: {"status": "healthy"}
```

### 2. Проверьте фронтенд
```bash
curl -I http://localhost:3000
# Должен вернуть: HTTP/1.1 200 OK
```

### 3. Проверьте nginx
```bash
curl -I http://localhost
# Должен вернуть: HTTP/1.1 200 OK
```

### 4. Проверьте домены
```bash
curl -I http://tvoi-kalkulyator.ru
curl -I http://твой-калькулятор.рф
```

## 🛠️ Управление сервисами:

### Запуск через systemd
```bash
# Копируем сервис
cp dieta-bot.service /etc/systemd/system/

# Перезагружаем systemd
systemctl daemon-reload

# Включаем автозапуск
systemctl enable dieta-bot.service

# Запускаем
systemctl start dieta-bot.service
```

### Проверка статуса
```bash
systemctl status dieta-bot.service
```

### Логи
```bash
# Логи сервиса
journalctl -u dieta-bot.service -f

# Логи nginx
tail -f /var/log/nginx/tvoi-kalkulyator.error.log

# Логи приложений
tail -f logs/api.log
tail -f logs/frontend.log
tail -f logs/bot.log
```

## 🔍 Диагностика проблем:

### Проблема: Сайт не открывается
```bash
# Проверьте nginx
systemctl status nginx
nginx -t

# Проверьте конфигурацию
cat /etc/nginx/sites-enabled/tvoi-kalkulyator

# Перезапустите nginx
systemctl restart nginx
```

### Проблема: API не отвечает
```bash
# Проверьте процесс
ps aux | grep improved_api_server

# Проверьте порт
netstat -tulpn | grep 8000

# Проверьте логи
tail -f logs/api.log
```

### Проблема: Фронтенд не отвечает
```bash
# Проверьте процесс
ps aux | grep "npm start"

# Проверьте порт
netstat -tulpn | grep 3000

# Проверьте логи
tail -f logs/frontend.log
```

## 📊 Финальная проверка:

После запуска все должно работать:

1. **Веб-сайт**: http://tvoi-kalkulyator.ru
2. **Альтернативный домен**: http://твой-калькулятор.рф
3. **API**: http://tvoi-kalkulyator.ru/api/health
4. **Telegram бот**: @tvoy_diet_bot

## 🎯 Команды для быстрого запуска:

```bash
# Полное исправление и запуск
./fix_and_start.sh

# Только исправление зависимостей
./fix_dependencies.sh

# Только запуск
./start_production.sh

# Проверка статуса
systemctl status dieta-bot.service
```

---

**Теперь все должно работать правильно! 🎉** 