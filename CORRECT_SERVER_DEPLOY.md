# Правильный деплой на сервер Timeweb Cloud

## Подключение к серверу
```bash
ssh root@5.129.198.80
```

## Шаг 1: Переход в папку проекта
```bash
# Переходим в папку /opt/dieta (не /opt/dieta/dieta!)
cd /opt/dieta

# Проверяем содержимое
ls -la
```

## Шаг 2: Скачивание и запуск скрипта деплоя
```bash
# Скачиваем новый скрипт деплоя
curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/server_deploy.sh

# Даем права на выполнение
chmod +x server_deploy.sh

# Запускаем деплой
./server_deploy.sh
```

## Что делает скрипт:
1. ✅ Проверяет текущую папку `/opt/dieta`
2. ✅ Клонирует проект если его нет
3. ✅ Обновляет проект из GitHub
4. ✅ Создает шаблон `.env` файла если нужно
5. ✅ Устанавливает Docker и Docker Compose
6. ✅ Останавливает старые контейнеры
7. ✅ Собирает и запускает новые контейнеры
8. ✅ Проверяет статус сервисов

## Шаг 3: Настройка .env файла
Если скрипт создал `.env` файл, отредактируйте его:
```bash
nano .env
```

### Заполните реальными значениями:
```env
# Telegram Bot
TG_TOKEN=ваш_реальный_токен_бота

# Database (Neon PostgreSQL) 
DATABASE_URL=postgresql://username:password@host:port/database

# AI Services
MISTRAL_API_KEY=ваш_ключ_mistral
GIGACHAT_CLIENT_SECRET=ваш_ключ_gigachat
GIGACHAT_CLIENT_ID=ваш_id_gigachat

# API Configuration
API_BASE_URL=http://5.129.198.80:8000
FRONTEND_URL=http://5.129.198.80:3000

# CalorieNinjas API (необязательно)
CALORIE_NINJAS_API_KEY=ваш_ключ_calorie_ninjas
```

## Шаг 4: Перезапуск после настройки .env
```bash
docker-compose restart
```

## Проверка работы
```bash
# Статус контейнеров
docker-compose ps

# Логи всех сервисов
docker-compose logs

# Логи конкретного сервиса
docker-compose logs api
docker-compose logs bot
docker-compose logs frontend
```

## Доступные адреса:
- **API:** http://5.129.198.80:8000
- **API Документация:** http://5.129.198.80:8000/docs
- **Веб-приложение:** http://5.129.198.80:3000
- **Health Check:** http://5.129.198.80:8000/health

## Команды управления:
```bash
# Перезапуск сервисов
docker-compose restart

# Остановка
docker-compose down

# Пересборка и запуск
docker-compose up --build -d

# Мониторинг логов в реальном времени
docker-compose logs -f
```

## Решение проблем:

### Если контейнеры не запускаются:
```bash
# Смотрим логи ошибок
docker-compose logs

# Полная очистка и пересборка
docker-compose down --remove-orphans
docker system prune -f
docker-compose up --build -d
```

### Если фронтенд не собирается:
```bash
# Проверяем логи фронтенда
docker-compose logs frontend

# Пересобираем только фронтенд
docker-compose up --build frontend
```

### Если API не отвечает:
```bash
# Проверяем health check
curl http://5.129.198.80:8000/health

# Смотрим логи API
docker-compose logs api
``` 