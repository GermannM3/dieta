# 🚀 Dieta Bot - Инструкции по запуску на сервере

## 📋 Быстрый старт

### 1. Клонирование и настройка
```bash
cd /opt
git clone <ваш-репозиторий> dieta
cd dieta
python3 -m venv venv
source venv/bin/activate
```

### 2. Исправление зависимостей (ОБЯЗАТЕЛЬНО!)
```bash
chmod +x fix_dependencies.sh
./fix_dependencies.sh
```

### 3. Настройка конфигурации
```bash
cp .env.example .env
nano .env  # Настройте переменные
```

### 4. Быстрая диагностика
```bash
python quick_server_fix.py
```

### 5. Запуск
```bash
chmod +x deploy_server.sh
./deploy_server.sh
```

## 🔧 Исправленные проблемы

### ✅ Конфликт зависимостей
- **Проблема:** `aiogram 3.4.1` требует `pydantic<2.6`, а `mistralai>=1.0.0` требует `pydantic>=2.10.3`
- **Решение:** Обновлены версии в `requirements.txt`:
  - `aiogram>=3.4,<4`
  - `fastapi>=0.115,<0.120`
  - `mistralai>=1.9,<2`

### ✅ Русские сообщения
- Все сообщения в скриптах остались на русском языке
- Эмодзи и статусы сохранены

### ✅ Автоматическое исправление
- Скрипт `fix_dependencies.sh` принудительно разрешает конфликты
- Скрипт `quick_server_fix.py` диагностирует и исправляет проблемы

## 📁 Структура файлов

```
dieta/
├── main.py                    # Основной файл бота
├── improved_api_server.py     # API сервер
├── requirements.txt           # Зависимости (исправлены)
├── .env                      # Конфигурация
├── deploy_server.sh          # Автоматическое развертывание
├── fix_dependencies.sh       # Исправление зависимостей
├── quick_server_fix.py       # Быстрая диагностика
├── dieta-bot.service         # Systemd сервис
└── SERVER_INSTRUCTIONS.md    # Подробные инструкции
```

## 🚀 Команды управления

### Запуск
```bash
# Автоматическое развертывание
./deploy_server.sh

# Ручной запуск
python start_all_services.py

# Через systemd
systemctl start dieta-bot.service
```

### Проверка статуса
```bash
# Статус сервиса
systemctl status dieta-bot.service

# Логи в реальном времени
journalctl -u dieta-bot.service -f

# Проверка API
curl http://localhost:8000/health

# Проверка фронтенда
curl -I http://localhost:3000
```

### Остановка/перезапуск
```bash
# Остановить
systemctl stop dieta-bot.service

# Перезапустить
systemctl restart dieta-bot.service
```

## 🛠️ Устранение неполадок

### Проблема: Конфликт зависимостей
```bash
./fix_dependencies.sh
```

### Проблема: Сервис не запускается
```bash
python quick_server_fix.py
journalctl -u dieta-bot.service -f
```

### Проблема: Порт занят
```bash
lsof -i :8000
lsof -i :3000
kill -9 <PID>
```

## 📊 Мониторинг

### Проверка ресурсов
```bash
# CPU и память
htop

# Дисковое пространство
df -h

# Сетевые соединения
netstat -tulpn
```

### Логи
```bash
# Все логи сервиса
journalctl -u dieta-bot.service

# Логи за последний час
journalctl -u dieta-bot.service --since "1 hour ago"

# Очистка старых логов
journalctl --vacuum-time=7d
```

## 🔒 Безопасность

### Файрвол
```bash
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # API
ufw allow 3000/tcp  # Frontend
ufw enable
```

### SSL сертификаты
```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d ваш-домен.com
```

## 📞 Поддержка

### Полезные команды
```bash
# Полная диагностика
python quick_server_fix.py

# Проверка конфигурации
python test_db_connection.py

# Проверка SMTP
python test_smtp.py

# Проверка премиум функций
python test_premium.py
```

### Логи для отладки
```bash
# Логи бота
journalctl -u dieta-bot.service -f

# Логи nginx
tail -f /var/log/nginx/error.log

# Логи системы
dmesg | tail -20
```

---

## 🎯 Что исправлено в этой версии

1. **✅ Конфликт зависимостей** - разрешен конфликт между `aiogram`, `fastapi` и `mistralai`
2. **✅ Русские сообщения** - все сообщения остались на русском языке
3. **✅ Автоматическое исправление** - скрипты для автоматического разрешения проблем
4. **✅ Улучшенная диагностика** - быстрая проверка всех компонентов
5. **✅ Стабильный запуск** - исправлены проблемы с systemd сервисом

**Готово к запуску! 🚀** 