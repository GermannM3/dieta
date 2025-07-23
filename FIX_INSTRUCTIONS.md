# 🔧 Инструкции по исправлению проблем на сервере

## ✅ Что исправлено:

1. **Исправлена конфигурация nginx** - заменены `api:8000` и `frontend:80` на `127.0.0.1:8000` и `127.0.0.1:3000`
2. **Исправлена диагностика** - правильные имена переменных в .env
3. **Исправлена проверка БД** - используется `engine.begin()` вместо `engine.connect()`
4. **Исправлена ошибка psutil** - правильный способ получения connections
5. **Создан скрипт тестирования** - `test_services.py` для ручной проверки

## 🚀 Пошаговое исправление на сервере:

### 1. Получите обновления
```bash
git pull
```

### 2. Активируйте окружение
```bash
source venv/bin/activate
```

### 3. Обновите зависимости
```bash
pip install --upgrade sqlalchemy asyncpg
```

### 4. Проверьте конфигурацию nginx
```bash
sudo nginx -t
```

### 5. Перезапустите nginx
```bash
sudo systemctl reload nginx
```

### 6. Запустите диагностику
```bash
python diagnose.py
```

### 7. Протестируйте сервисы по отдельности
```bash
python test_services.py
```

### 8. Если все тесты прошли, запустите все сервисы
```bash
python start_all.py
```

## 🔍 Ручное тестирование (если нужно):

### Тест API:
```bash
# Терминал 1
uvicorn improved_api_server:app --host 0.0.0.0 --port 8000 --reload
```

### Тест бота:
```bash
# Терминал 2
python main.py
```

### Тест фронтенда:
```bash
# Терминал 3
cd calorie-love-tracker
npm start
```

## 🌐 Проверка работы:

```bash
# API
curl http://localhost:8000/health

# Фронтенд
curl -I http://localhost:3000

# Сайт
curl -I http://tvoi-kalkulyator.ru
```

## 🚨 Возможные проблемы и решения:

### 1. Ошибка "host not found in upstream"
- ✅ Исправлено: заменены upstream на 127.0.0.1

### 2. Ошибка "AsyncConnection object does not support context manager"
- ✅ Исправлено: используется `engine.begin()` вместо `engine.connect()`

### 3. Ошибка "invalid attr name 'connections'"
- ✅ Исправлено: правильный способ получения connections в psutil

### 4. Переменные окружения не найдены
- ✅ Исправлено: правильные имена переменных (TG_TOKEN вместо BOT_TOKEN)

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

---

**После выполнения всех шагов проект должен работать корректно! 🎉** 