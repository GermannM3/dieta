# Команды для работы с Docker

## Основные команды для логов

### Просмотр логов всех сервисов:
```bash
docker-compose logs
``

docker-compose down
docker system prune -af --volumes
docker-compose build --no-cache
docker-compose up -d

### Просмотр логов конкретного сервиса:
```bash
docker-compose logs api
docker-compose logs bot
docker-compose logs frontend
docker-compose logs nginx
```

### Просмотр логов в реальном времени:
```bash


docker-compose logs -f bot
```

### Просмотр последних N строк:
```bash
docker-compose logs --tail=100 bot
```

## Управление контейнерами

### Статус контейнеров:
```bash
docker-compose ps
```

### Остановка всех контейнеров:
```bash
docker-compose down
```

### Запуск всех контейнеров:
```bash
docker-compose up -d
```

### Перезапуск конкретного сервиса:
```bash
docker-compose restart bot
docker-compose restart api
```

### Перезапуск всех сервисов:
```bash
docker-compose restart
```

## Отладка

### Войти в контейнер:
```bash
docker-compose exec bot bash
docker-compose exec api bash
```

### Проверить переменные окружения:
```bash
docker-compose exec bot env
```

### Проверить файлы в контейнере:
```bash
docker-compose exec bot ls -la
```

## Полезные команды

### Очистить логи:
```bash
docker-compose logs --tail=0
```

### Просмотр использования ресурсов:
```bash
docker stats
```

### Просмотр образов:
```bash
docker images
```

### Очистка неиспользуемых ресурсов:
```bash
docker system prune
``` 