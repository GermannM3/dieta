# ⚡ Быстрый деплой Твой Диетолог

## 🔑 Данные сервера
- **IP**: 5.129.198.80
- **Пользователь**: root  
- **Пароль**: z.BqR?PLrJ8QZ8
- **GitHub**: https://github.com/GermannM3/dieta.git

## 🚀 Автоматический деплой (рекомендуется)

```bash
# 1. Подключение к серверу
ssh root@5.129.198.80

# 2. Автоматический деплой (скрипт сам установит Docker, настроит Nginx)
curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/auto-deploy.sh
chmod +x auto-deploy.sh
./auto-deploy.sh
```

**⚠️ При первом запуске:**
Скрипт остановится и попросит настроить `.env` файл:

```bash
# 3. Настройка переменных окружения
nano /opt/dieta/.env
```

**🔑 Обязательно заполните:**
- `TG_TOKEN` - токен бота от @BotFather
- `DATABASE_URL` - строка подключения Neon PostgreSQL
- `MISTRAL_API_KEY` - ключ Mistral AI
- `ADMIN_ID` - ваш Telegram ID

```bash
# 4. Повторный запуск после настройки .env
cd /opt/dieta
./auto-deploy.sh
```

## 🔄 Обновление (когда есть изменения в GitHub)

```bash
# Подключение к серверу
ssh root@5.129.198.80

# Автоматическое обновление
cd /opt/dieta
./auto-deploy.sh
```

## ✅ Результат
После деплоя будут доступны:
- **Веб-приложение**: http://5.129.198.80
- **API сервер**: http://5.129.198.80/api/
- **API документация**: http://5.129.198.80/docs
- **Health check**: http://5.129.198.80/health
- **Telegram бот**: @tvoy_diet_bot

## 🔧 Мониторинг

### Быстрая проверка статуса
```bash
cd /opt/dieta
docker-compose ps
```

### Логи сервисов
```bash
# Все логи
docker-compose logs -f

# Отдельные сервисы
docker-compose logs -f api      # API сервер
docker-compose logs -f bot      # Telegram бот
docker-compose logs -f frontend # React веб-приложение
```

### Управление сервисами
```bash
cd /opt/dieta

# Перезапуск всех сервисов
docker-compose restart

# Перезапуск отдельного сервиса
docker-compose restart bot

# Остановка
docker-compose down

# Запуск
docker-compose up -d
```

## 🚨 Решение проблем

### Проблема: Контейнеры не запускаются
```bash
# Проверьте логи
docker-compose logs

# Пересоберите образы
docker-compose down
docker-compose up --build -d
```

### Проблема: База данных недоступна
1. Проверьте `DATABASE_URL` в `.env`
2. Убедитесь что Neon PostgreSQL доступна
3. Проверьте логи: `docker-compose logs api`

### Проблема: Telegram бот не отвечает
1. Проверьте `TG_TOKEN` в `.env`
2. Проверьте логи: `docker-compose logs bot`
3. Перезапустите: `docker-compose restart bot`

## 📋 Архитектура деплоя

Система разворачивается в Docker контейнерах:
- **API контейнер**: FastAPI сервер (порт 8000)
- **Bot контейнер**: Telegram бот Python
- **Frontend контейнер**: React приложение (порт 3000)
- **Nginx**: Проксирует запросы и раздает статику

## 🔄 Автоматические возможности

✅ **Автоустановка Docker** и Docker Compose  
✅ **Автонастройка Nginx** с проксированием  
✅ **Автоклонирование** кода с GitHub  
✅ **Автопересборка** при обновлениях  
✅ **Health checks** для мониторинга  
✅ **Автоперезапуск** при сбоях  

---

📖 **Подробная документация**: [TIMEWEB_DEPLOY.md](TIMEWEB_DEPLOY.md) 