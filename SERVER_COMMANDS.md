# Команды для сервера

## 1. Обновить код
```bash
cd /opt/dieta
git stash
git pull
```

## 2. Остановить контейнеры
```bash
docker-compose down
```

## 3. Очистить Docker
```bash
docker system prune -af --volumes
```

## 4. Пересобрать контейнеры
```bash
docker-compose build --no-cache
```

## 5. Запустить контейнеры
```bash
docker-compose up -d
```

## 6. Проверить статус
```bash
docker-compose ps
```

## 7. Проверить API
```bash
curl http://5.129.198.80:8000/health
```

## 8. Проверить frontend
```bash
curl http://5.129.198.80:3000
```

## 9. Проверить HTTPS домены
```bash
curl -I https://твой-калькулятор.рф
curl -I https://tvoi-kalkulyator.ru
```

## 10. Проверить HTTP → HTTPS редирект
```bash
curl -I http://твой-калькулятор.рф
curl -I http://tvoi-kalkulyator.ru
```

## 11. Посмотреть логи
```bash
docker-compose logs api
docker-compose logs bot
docker-compose logs nginx
```

## Быстрая последовательность:
```bash
cd /opt/dieta && git stash && git pull && docker-compose down && docker system prune -af --volumes && docker-compose build --no-cache && docker-compose up -d
```

## Проверка SSL сертификатов:
```bash
ls -la /etc/letsencrypt/live/твой-калькулятор.рф/
``` 