# 🐳 Docker Setup Complete!

## ✅ Что сделано:

### 1. **Dockerfile** - для Python приложений (бот + API)
- Базовый образ Python 3.11
- Все необходимые зависимости
- Поддержка PostgreSQL (asyncpg + psycopg2)

### 2. **Dockerfile.frontend** - для React приложения
- Multi-stage build для оптимизации
- Nginx для продакшн сервера
- Оптимизация статических файлов

### 3. **docker-compose.yml** - полный продакшн стек
- PostgreSQL база данных
- FastAPI backend
- Telegram bot
- React frontend
- Nginx reverse proxy с SSL

### 4. **docker-compose.dev.yml** - для разработки
- Использует Neon DB (внешняя БД)
- Hot reload для разработки
- Монтирование локальных файлов

### 5. **Конфигурации Nginx**
- nginx.conf - для фронтенда
- nginx-prod.conf - продакшн с SSL

## 🚀 Как запустить:

### Вариант 1: Разработка (с Neon DB)
```bash
# 1. Создайте .env файл
cp env.example .env
# Отредактируйте и добавьте ваши ключи

# 2. Запустите
docker-compose -f docker-compose.dev.yml up -d

# 3. Проверьте
docker-compose -f docker-compose.dev.yml ps
```

### Вариант 2: Продакшн (все включено)
```bash
# 1. Создайте .env файл
cp env.example .env

# 2. Запустите все сервисы
docker-compose up -d --build

# 3. Инициализируйте БД (первый раз)
docker-compose exec api python -c "from database.init_database import init_db; import asyncio; asyncio.run(init_db())"
```

## 📝 Необходимые переменные в .env:
```env
TG_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_id
DATABASE_URL=postgresql+asyncpg://...  # Для Neon
MISTRAL_API_KEY=your_mistral_key
CALORIE_NINJAS_API_KEY=your_calorie_key
```

## 🌐 Доступные сервисы после запуска:

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000 (продакшн) или http://localhost:5173 (dev)
- **Telegram Bot**: Ваш бот в Telegram

## 📊 Управление:

```bash
# Логи
docker-compose logs -f bot
docker-compose logs -f api

# Перезапуск
docker-compose restart bot

# Остановка
docker-compose down

# Полная очистка
docker-compose down -v
```

## 🎯 Готово к деплою!

Проект полностью контейнеризован и готов к развертыванию на любом сервере с Docker.

Подробная инструкция в файле: **DOCKER_DEPLOYMENT.md**

---
*Все файлы созданы и настроены. Можете проверять!* 