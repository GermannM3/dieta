# 🐳 Docker Deployment Guide - Диетолог Bot

## 📋 Содержание
1. [Быстрый старт](#быстрый-старт)
2. [Подготовка](#подготовка)
3. [Локальная разработка](#локальная-разработка)
4. [Продакшн деплой](#продакшн-деплой)
5. [Управление](#управление)
6. [Решение проблем](#решение-проблем)

## 🚀 Быстрый старт

### Для локальной разработки (с Neon DB):
```bash
# 1. Клонируйте репозиторий
git clone <your-repo>
cd ai_tgBot-main

# 2. Создайте .env файл
cp env.example .env
# Отредактируйте .env и добавьте ваши ключи

# 3. Запустите через Docker Compose
docker-compose -f docker-compose.dev.yml up -d

# 4. Проверьте статус
docker-compose -f docker-compose.dev.yml ps
```

### Для продакшена:
```bash
# Запустите все сервисы
docker-compose up -d

# Или с пересборкой
docker-compose up -d --build
```

## 📝 Подготовка

### 1. Создайте .env файл
```env
# Telegram Bot
TG_TOKEN=your_bot_token_from_botfather
ADMIN_ID=your_telegram_user_id

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@host.neon.tech/dbname

# API Keys
MISTRAL_API_KEY=your_mistral_key
CALORIE_NINJAS_API_KEY=your_calorie_ninjas_key
```

### 2. Получите необходимые ключи:
- **TG_TOKEN**: Создайте бота через [@BotFather](https://t.me/botfather)
- **ADMIN_ID**: Узнайте через [@userinfobot](https://t.me/userinfobot)
- **DATABASE_URL**: Создайте БД на [Neon.tech](https://neon.tech)
- **MISTRAL_API_KEY**: Получите на [Mistral AI](https://mistral.ai)
- **CALORIE_NINJAS_API_KEY**: На [CalorieNinjas](https://calorieninjas.com)

## 🔧 Локальная разработка

### Использование docker-compose.dev.yml:
```bash
# Запуск с Neon DB (рекомендуется)
docker-compose -f docker-compose.dev.yml up -d

# Просмотр логов
docker-compose -f docker-compose.dev.yml logs -f bot
docker-compose -f docker-compose.dev.yml logs -f api

# Перезапуск после изменений
docker-compose -f docker-compose.dev.yml restart bot
```

### Доступные сервисы:
- 🤖 Telegram Bot: Ваш бот в Telegram
- 🔧 API Server: http://localhost:8000
- 📊 API Docs: http://localhost:8000/docs
- 🌐 Frontend: http://localhost:5173

## 🌐 Продакшн деплой

### 1. С локальной PostgreSQL:
```bash
# Запустите все сервисы включая БД
docker-compose up -d

# Инициализируйте БД (первый раз)
docker-compose exec api python -c "from database.init_database import init_db; import asyncio; asyncio.run(init_db())"
```

### 2. Настройка домена:
Отредактируйте `nginx-prod.conf`:
```nginx
server_name dietolog.example.com;  # Замените на ваш домен
```

### 3. SSL сертификаты:
```bash
# Создайте директорию для SSL
mkdir ssl

# Вариант 1: Let's Encrypt (рекомендуется)
docker run -it --rm \
  -v $(pwd)/ssl:/etc/letsencrypt \
  certbot/certbot certonly \
  --standalone \
  -d dietolog.example.com

# Вариант 2: Самоподписанный (для тестов)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem
```

### 4. Запуск с Nginx:
```bash
docker-compose up -d nginx
```

## 📊 Управление

### Просмотр логов:
```bash
# Все логи
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f bot
docker-compose logs -f api
```

### Обновление кода:
```bash
# Остановите сервисы
docker-compose down

# Обновите код
git pull

# Пересоберите и запустите
docker-compose up -d --build
```

### Backup базы данных:
```bash
# Для локальной PostgreSQL
docker-compose exec postgres pg_dump -U dietolog dietolog_db > backup.sql

# Восстановление
docker-compose exec -T postgres psql -U dietolog dietolog_db < backup.sql
```

## 🔍 Решение проблем

### Бот не отвечает:
```bash
# Проверьте логи
docker-compose logs bot

# Проверьте переменные окружения
docker-compose exec bot env | grep TG_TOKEN
```

### API недоступен:
```bash
# Проверьте статус
docker-compose ps api

# Проверьте подключение к БД
docker-compose exec api python -c "from database.init_database import engine; print('DB OK')"
```

### Frontend не загружается:
```bash
# Пересоберите frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Очистка и перезапуск:
```bash
# Полная очистка
docker-compose down -v
docker system prune -a

# Заново
docker-compose up -d --build
```

## 🚢 Деплой на VPS

### 1. Установите Docker:
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### 2. Установите Docker Compose:
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Клонируйте проект:
```bash
git clone <your-repo>
cd ai_tgBot-main
```

### 4. Настройте и запустите:
```bash
# Создайте .env
nano .env

# Запустите
docker-compose up -d
```

## 📱 Мониторинг

### Статус сервисов:
```bash
# Общий статус
docker-compose ps

# Использование ресурсов
docker stats
```

### Автоматический перезапуск:
Все сервисы настроены с `restart: unless-stopped`

### Логирование:
Логи сохраняются в директории `./logs/`

## 🎯 Готово!

Ваш бот-диетолог теперь работает в Docker! 

Проверьте:
- ✅ Бот отвечает в Telegram
- ✅ API доступен по http://localhost:8000/docs
- ✅ Frontend работает на http://localhost:3000

---
*Для помощи создайте issue в репозитории* 