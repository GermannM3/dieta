# 🎯 Финальные инструкции для запуска на сервере

## ✅ Что исправлено:

1. **Исправлен скрипт `fix_dependencies.sh`** - убрана ошибка с версией fastapi
2. **Создан простой `start_all.py`** - один скрипт запускает все сервисы
3. **Добавлен `diagnose.py`** - для диагностики проблем
4. **Обновлены инструкции** - простые и понятные

## 🚀 Как запустить на сервере:

### 1. Подключитесь к серверу
```bash
ssh root@5.129.198.80
cd /opt/dieta
```

### 2. Получите обновления
```bash
git pull
```

### 3. Активируйте виртуальное окружение
```bash
source venv/bin/activate
```

### 4. Запустите диагностику (если нужно)
```bash
python diagnose.py
```

### 5. Исправьте зависимости (если нужно)
```bash
chmod +x fix_dependencies.sh
./fix_dependencies.sh
```

### 6. Запустите все сервисы
```bash
python start_all.py
```

## 🌐 Что будет доступно:

- **Веб-сайт**: http://tvoi-kalkulyator.ru
- **Альтернативный домен**: http://твой-калькулятор.рф
- **API**: http://tvoi-kalkulyator.ru/api/health
- **Telegram бот**: @tvoy_diet_bot

## 📊 Мониторинг:

```bash
# Общий лог
tail -f start_all.log

# Отдельные логи
tail -f logs/api.log
tail -f logs/frontend.log
tail -f logs/bot.log
tail -f /var/log/nginx/tvoi-kalkulyator.error.log
```

## 🔍 Проверка работы:

```bash
# API
curl http://localhost:8000/health

# Фронтенд
curl -I http://localhost:3000

# Сайт
curl -I http://tvoi-kalkulyator.ru
```

## 🛑 Остановка:

Нажмите `Ctrl+C` в терминале где запущен скрипт.

## 🚨 Если проблемы:

1. **Диагностика**: `python diagnose.py`
2. **Логи**: `tail -f start_all.log`
3. **Перезапуск**: `python start_all.py`

## 📝 Что делает `start_all.py`:

1. 🛑 Останавливает старые процессы
2. 🚀 Запускает API сервер (порт 8000)
3. 🌐 Запускает фронтенд (порт 3000)
4. 🔧 Настраивает и запускает nginx (порт 80)
5. 🤖 Запускает Telegram бота
6. 🔍 Проверяет все сервисы
7. 📊 Показывает логи и статус

---

**Всё готово! Просто запустите `python start_all.py` и всё заработает! 🎉** 