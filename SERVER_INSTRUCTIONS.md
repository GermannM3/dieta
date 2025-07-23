# 🚀 Инструкции по запуску Dieta Bot на сервере

## 📋 Предварительные требования

1. **Ubuntu Server 20.04+**
2. **Python 3.12+**
3. **Git**
4. **Root доступ**

## 🔧 Установка и настройка

### 1. Клонирование проекта
```bash
cd /opt
git clone <ваш-репозиторий> dieta
cd dieta
```

### 2. Создание виртуального окружения
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Исправление конфликтов зависимостей
```bash
# Делаем скрипт исполняемым
chmod +x fix_dependencies.sh

# Запускаем исправление зависимостей
./fix_dependencies.sh
```

### 4. Настройка переменных окружения
```bash
# Копируем пример конфигурации
cp .env.example .env

# Редактируем конфигурацию
nano .env
```

**Обязательные переменные в .env:**
```env
# Telegram Bot
TG_TOKEN=ваш_токен_бота
ADMIN_ID=ваш_id_админа

# База данных PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# YooKassa
YOOKASSA_SHOP_ID=ваш_shop_id
YOOKASSA_SECRET_KEY=ваш_секретный_ключ

# SMTP для email
SMTP_SERVER=smtp.rambler.ru
SMTP_PORT=465
SMTP_USERNAME=ваш_email@rambler.ru
SMTP_PASSWORD=ваш_пароль
FROM_EMAIL=ваш_email@rambler.ru
```

### 5. Тестирование конфигурации
```bash
# Проверяем подключение к БД
python test_db_connection.py

# Проверяем SMTP
python test_smtp.py
```

## 🚀 Запуск на сервере

### Вариант 1: Автоматическое развертывание
```bash
# Делаем скрипт исполняемым
chmod +x deploy_server.sh

# Запускаем развертывание
./deploy_server.sh
```

### Вариант 2: Ручной запуск
```bash
# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем все сервисы
python start_all_services.py
```

### Вариант 3: Запуск через systemd
```bash
# Копируем файл сервиса
cp dieta-bot.service /etc/systemd/system/

# Перезагружаем systemd
systemctl daemon-reload

# Включаем автозапуск
systemctl enable dieta-bot.service

# Запускаем сервис
systemctl start dieta-bot.service
```

## 📊 Управление сервисом

### Проверка статуса
```bash
systemctl status dieta-bot.service
```

### Просмотр логов
```bash
# Логи в реальном времени
journalctl -u dieta-bot.service -f

# Последние 100 строк логов
journalctl -u dieta-bot.service -n 100
```

### Остановка/перезапуск
```bash
# Остановить сервис
systemctl stop dieta-bot.service

# Перезапустить сервис
systemctl restart dieta-bot.service
```

## 🔍 Проверка работоспособности

### 1. Проверка API сервера
```bash
curl http://ваш_ip:8000/health
```
**Ожидаемый ответ:** `{"status": "healthy"}`

### 2. Проверка фронтенда
```bash
curl -I http://ваш_ip:3000
```
**Ожидаемый ответ:** `HTTP/1.1 200 OK`

### 3. Проверка бота
```bash
# Отправьте сообщение боту @tvoy_diet_bot
# Должен ответить приветствием
```

## 🛠️ Устранение неполадок

### Проблема: Конфликт зависимостей
```bash
# Запустите скрипт исправления
./fix_dependencies.sh
```

### Проблема: Сервис не запускается
```bash
# Проверьте логи
journalctl -u dieta-bot.service -f

# Проверьте конфигурацию
python test_db_connection.py
```

### Проблема: Порт занят
```bash
# Найдите процесс на порту
lsof -i :8000
lsof -i :3000

# Остановите процесс
kill -9 <PID>
```

### Проблема: Нет доступа к базе данных
```bash
# Проверьте переменные окружения
cat .env | grep DATABASE

# Проверьте подключение
python test_db_connection.py
```

## 📝 Полезные команды

### Очистка логов
```bash
journalctl --vacuum-time=7d
```

### Проверка использования ресурсов
```bash
# CPU и память
htop

# Дисковое пространство
df -h

# Сетевые соединения
netstat -tulpn
```

### Резервное копирование
```bash
# База данных
pg_dump your_database > backup.sql

# Файлы проекта
tar -czf dieta_backup_$(date +%Y%m%d).tar.gz /opt/dieta
```

## 🔒 Безопасность

### Настройка файрвола
```bash
# Разрешаем только нужные порты
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # API
ufw allow 3000/tcp  # Frontend

# Включаем файрвол
ufw enable
```

### SSL сертификаты
```bash
# Установка Certbot
apt install certbot python3-certbot-nginx

# Получение сертификата
certbot --nginx -d ваш-домен.com
```

## 📞 Поддержка

При возникновении проблем:

1. **Проверьте логи:** `journalctl -u dieta-bot.service -f`
2. **Проверьте конфигурацию:** `python test_db_connection.py`
3. **Перезапустите сервис:** `systemctl restart dieta-bot.service`
4. **Обратитесь к документации:** `README.md`

---

**Успешного развертывания! 🎉** 