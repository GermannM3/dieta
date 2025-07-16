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

# 2. Настройка переменных окружения (только при первом деплое)
curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/setup-env.sh
chmod +x setup-env.sh
./setup-env.sh

# 3. Автоматический деплой
curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/auto-deploy.sh
chmod +x auto-deploy.sh
./auto-deploy.sh
```

## 🔄 Обновление (когда есть изменения в GitHub)

```bash
# Подключение к серверу
ssh root@5.129.198.80

# Обновление
cd /opt/dieta && ./auto-deploy.sh
```

## ✅ Результат
После деплоя будут доступны:
- **Веб-приложение**: http://5.129.198.80
- **API сервер**: http://5.129.198.80:8000
- **API документация**: http://5.129.198.80/docs
- **Telegram бот**: @tvoy_diet_bot

## 🔧 Мониторинг
```bash
# Логи всех сервисов
docker logs dieta-bot -f      # Telegram бот
docker logs dieta-api -f      # API сервер
docker logs diet-webapp -f    # Веб-приложение

# Статус контейнеров
docker ps

# Использование ресурсов
docker stats
```

## 🚨 Важно
- Система автоматически тянет обновления с GitHub
- Все сервисы (бот + API + веб-приложение) разворачиваются одновременно
- Конфигурация в `/opt/dieta/.env` 