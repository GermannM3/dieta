# 🚀 Деплой на Timeweb Cloud

## 📋 Предварительные требования

### 1. Подготовка токенов и ключей
Убедитесь, что у вас есть:
- **TG_TOKEN** - токен Telegram бота от @BotFather
- **DATABASE_URL** - строка подключения к Neon PostgreSQL  
- **MISTRAL_API_KEY** - ключ API Mistral AI
- **GIGACHAT_* ключи** - для GigaChat API (опционально)

### 2. Доступ к серверу
- **IP**: 5.129.198.80
- **Пользователь**: root
- **Пароль**: z.BqR?PLrJ8QZ8

## 🔧 Автоматический деплой

### Шаг 1: Подключение к серверу
```bash
ssh root@5.129.198.80
```

### Шаг 2: Автоматический деплой
```bash
# Скачиваем и запускаем скрипт деплоя
curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/auto-deploy.sh
chmod +x auto-deploy.sh
./auto-deploy.sh
```

### Шаг 3: Настройка переменных окружения
Если это первый запуск, скрипт создаст файл `.env` и остановится:

```bash
# Редактируем конфигурацию
nano /opt/dieta/.env
```

**Заполните обязательные поля:**
```env
# Telegram Bot Configuration
TG_TOKEN=your_telegram_bot_token_from_botfather
ADMIN_ID=your_telegram_id_number

# Database Configuration (используйте вашу Neon DB)
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# AI API Keys
MISTRAL_API_KEY=your_mistral_api_key

# GigaChat API (опционально)
GIGACHAT_CLIENT_ID=your_gigachat_client_id
GIGACHAT_AUTH_KEY=your_gigachat_auth_key
GIGACHAT_ACCESS_TOKEN=your_gigachat_access_token

# CalorieNinjas API (опционально)
CALORIE_NINJAS_API_KEY=your_calorie_ninjas_api_key
```

### Шаг 4: Повторный запуск деплоя
После настройки `.env`:
```bash
cd /opt/dieta
./auto-deploy.sh
```

## ✅ Результат деплоя

После успешного деплоя будут доступны:

### 🌐 Веб-интерфейс
- **URL**: http://5.129.198.80
- **Описание**: React веб-приложение для управления питанием

### 🔗 API сервер  
- **URL**: http://5.129.198.80/api/
- **Документация**: http://5.129.198.80/docs
- **Health check**: http://5.129.198.80/health

### 🤖 Telegram бот
- **Username**: @tvoy_diet_bot
- **Функции**: Полный функционал диетолога

## 📊 Управление сервисами

### Просмотр статуса
```bash
cd /opt/dieta
docker-compose ps
```

### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Отдельные сервисы
docker-compose logs -f api      # API сервер
docker-compose logs -f bot      # Telegram бот  
docker-compose logs -f frontend # Веб-приложение
```

### Перезапуск сервисов
```bash
cd /opt/dieta

# Все сервисы
docker-compose restart

# Отдельные сервисы
docker-compose restart api
docker-compose restart bot
docker-compose restart frontend
```

### Остановка/запуск
```bash
cd /opt/dieta

# Остановка
docker-compose down

# Запуск
docker-compose up -d

# Пересборка и запуск
docker-compose up --build -d
```

## 🔄 Обновление

### Автоматическое обновление
```bash
cd /opt/dieta
./auto-deploy.sh
```

### Ручное обновление
```bash
cd /opt/dieta

# Получение последних изменений
git pull origin main

# Пересборка и перезапуск
docker-compose up --build -d
```

## 🛠️ Решение проблем

### Проблема: Контейнеры не запускаются
```bash
# Проверьте логи
docker-compose logs

# Проверьте .env файл
cat /opt/dieta/.env

# Пересоберите образы
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Проблема: База данных недоступна
```bash
# Проверьте подключение к Neon
curl -I "ваш_DATABASE_URL"

# Проверьте логи API
docker-compose logs api
```

### Проблема: Telegram бот не отвечает
```bash
# Проверьте токен бота
echo $TG_TOKEN

# Проверьте логи бота
docker-compose logs bot

# Перезапустите бота
docker-compose restart bot
```

## 🔐 Безопасность

### Файл .env
- Никогда не добавляйте `.env` в git
- Регулярно обновляйте API ключи
- Ограничьте доступ к серверу

### Nginx
Сервер автоматически настраивает Nginx для:
- Проксирование запросов к API и фронтенду
- Обслуживание статических файлов
- Базовая защита от DDoS

## 📈 Мониторинг

### Системные ресурсы
```bash
# Использование ресурсов контейнерами
docker stats

# Место на диске
df -h

# Системная нагрузка
top
```

### Логи системы
```bash
# Системные логи
journalctl -u nginx -f
journalctl -u docker -f

# Логи приложения
tail -f /opt/dieta/logs/*.log
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи сервисов
2. Убедитесь в корректности .env
3. Перезапустите проблемный сервис
4. Обратитесь к разработчику с логами

---

**Версия**: 1.0  
**Дата**: 2025-01-17  
**Автор**: Диетолог-бот команда 