# Развертывание Dieta Bot на сервере

## Быстрый запуск

### 1. Подготовка сервера
```bash
# Подключитесь к серверу
ssh root@5.129.198.80

# Перейдите в директорию проекта
cd /opt/dieta

# Активируйте виртуальное окружение
source venv/bin/activate
```

### 2. Автоматическое развертывание
```bash
# Сделайте скрипт исполняемым
chmod +x deploy_server.sh

# Запустите развертывание
./deploy_server.sh
```

### 3. Проверка работы
```bash
# Статус сервиса
systemctl status dieta-bot.service

# Логи в реальном времени
journalctl -u dieta-bot.service -f
```

## Ручной запуск (если автоматический не работает)

### 1. Остановка старых процессов
```bash
# Остановите все процессы
pkill -f "main.py" || true
pkill -f "improved_api_server.py" || true
pkill -f "npm start" || true
pkill -f "nginx" || true
```

### 2. Проверка зависимостей
```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Проверьте подключение к БД
python test_db_connection.py
```

### 3. Запуск всех сервисов
```bash
# Запустите все сервисы через скрипт
python start_all_services.py
```

### 4. Проверка работы
```bash
# Проверьте, что процессы запущены
ps aux | grep -E "(main.py|improved_api_server.py|npm|nginx)"

# Проверьте порты
netstat -tlnp | grep -E "(8000|3000|80)"
```

## Настройка systemd сервиса

### 1. Установка сервиса
```bash
# Скопируйте файл сервиса
cp dieta-bot.service /etc/systemd/system/

# Перезагрузите systemd
systemctl daemon-reload

# Включите автозапуск
systemctl enable dieta-bot.service
```

### 2. Управление сервисом
```bash
# Запуск
systemctl start dieta-bot.service

# Остановка
systemctl stop dieta-bot.service

# Перезапуск
systemctl restart dieta-bot.service

# Статус
systemctl status dieta-bot.service

# Логи
journalctl -u dieta-bot.service -f
```

## Проверка работы сервисов

### 1. API сервер
```bash
# Проверьте health endpoint
curl http://5.129.198.80:8000/health

# Ожидаемый ответ:
# {"status": "healthy", "database": "connected"}
```

### 2. Фронтенд
```bash
# Проверьте доступность фронтенда
curl -I http://5.129.198.80:3000

# Должен вернуть HTTP 200
```

### 3. Nginx
```bash
# Проверьте статус nginx
systemctl status nginx

# Проверьте конфигурацию
nginx -t
```

### 4. Бот
```bash
# Проверьте логи бота
tail -f bot_debug.log

# Должны быть сообщения о подключении к Telegram
```

## Мониторинг и логи

### 1. Основные логи
```bash
# Логи systemd сервиса
journalctl -u dieta-bot.service -f

# Логи API сервера
tail -f api_server.log

# Логи бота
tail -f bot_debug.log

# Логи всех сервисов
tail -f services.log
```

### 2. Мониторинг процессов
```bash
# Список всех процессов
ps aux | grep -E "(main.py|improved_api_server.py|npm|nginx)"

# Использование портов
netstat -tlnp | grep -E "(8000|3000|80)"

# Использование ресурсов
htop
```

## Устранение неполадок

### 1. Сервис не запускается
```bash
# Проверьте статус
systemctl status dieta-bot.service

# Проверьте логи
journalctl -u dieta-bot.service -n 50

# Проверьте права доступа
ls -la /opt/dieta/
ls -la /opt/dieta/venv/bin/python
```

### 2. Проблемы с базой данных
```bash
# Проверьте подключение
python test_db_connection.py

# Проверьте переменные окружения
cat .env | grep DATABASE_URL
```

### 3. Проблемы с YooKassa
```bash
# Проверьте webhook
curl -X POST http://5.129.198.80:8000/api/payment/yookassa/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Проверьте логи API
tail -f api_server.log | grep yookassa
```

### 4. Проблемы с портами
```bash
# Проверьте, какие процессы используют порты
lsof -i :8000
lsof -i :3000
lsof -i :80

# Убейте процессы, если нужно
kill -9 <PID>
```

## Обновление кода

### 1. Остановка сервиса
```bash
systemctl stop dieta-bot.service
```

### 2. Обновление кода
```bash
# Если используете git
git pull origin main

# Или скопируйте файлы вручную
```

### 3. Перезапуск
```bash
systemctl start dieta-bot.service
systemctl status dieta-bot.service
```

## Контакты и поддержка

При возникновении проблем:
1. Проверьте логи: `journalctl -u dieta-bot.service -f`
2. Проверьте статус сервисов: `systemctl status dieta-bot.service`
3. Проверьте подключение к БД: `python test_db_connection.py`
4. Проверьте доступность API: `curl http://5.129.198.80:8000/health` 