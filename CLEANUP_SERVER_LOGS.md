# 🧹 ОЧИСТКА ЛОГОВ DOCKER НА СЕРВЕРЕ

## 🎯 Проблема
Docker контейнеры (особенно фронтенд) **захламляют диск** логами без ограничений.

---

## ⚡ КОМАНДЫ ДЛЯ СЕРВЕРА (выполнять последовательно)

### 🔌 Шаг 1: Подключение к серверу
```bash
ssh root@5.129.198.80
# Пароль: z.BqR?PLrJ8QZ8
```

### 📊 Шаг 2: Диагностика - проверка текущего состояния
```bash
# Переходим в проект
cd /opt/dieta

# Проверяем использование диска
df -h /

# Проверяем размер логов Docker (это ГЛАВНЫЙ пожиратель места!)
du -sh /var/lib/docker/containers/*/

# Общий размер логов
du -sh /var/lib/docker/containers/

# Статус контейнеров
docker-compose ps

# Проверяем логи бота (почему он падает)
docker logs dieta-bot-1 --tail 100
```

---

## 🗑️ Шаг 3: ОЧИСТКА ЛОГОВ

### Вариант A: Безопасная очистка (рекомендуется)

```bash
cd /opt/dieta

# Останавливаем контейнеры
docker-compose stop

# Очищаем логи (обнуляем файлы, не удаляя их)
truncate -s 0 /var/lib/docker/containers/*/*-json.log

# Проверяем результат
du -sh /var/lib/docker/containers/

# Запускаем контейнеры обратно
docker-compose up -d

# Проверяем статус
docker-compose ps
```

### Вариант B: Полная очистка Docker (более агрессивно)

```bash
cd /opt/dieta

# Останавливаем всё
docker-compose down

# Очищаем неиспользуемые данные (контейнеры, сети, образы)
docker system prune -a -f

# Очищаем volumes (если не нужны данные)
# ⚠️ ВНИМАНИЕ: Удалит данные в volumes!
# docker system prune -a -f --volumes

# Проверяем освобожденное место
docker system df

# Запускаем заново
docker-compose up -d
```

---

## ⚙️ Шаг 4: ПРИМЕНИТЬ НОВЫЕ НАСТРОЙКИ (ограничение логов)

```bash
cd /opt/dieta

# Скачать обновленные файлы с GitHub
git stash
git pull origin main

# Проверить что в docker-compose.yml есть ограничения на логи
grep -A 3 "logging:" docker-compose.yml

# Пересобрать контейнеры с новыми настройками
docker-compose down
docker-compose up -d --build

# Проверить настройки логирования контейнеров
docker inspect dieta-bot-1 | grep -A 10 "LogConfig"
docker inspect dieta-frontend-1 | grep -A 10 "LogConfig"
```

Должны увидеть:
```json
"LogConfig": {
    "Type": "json-file",
    "Config": {
        "max-size": "10m",
        "max-file": "3"
    }
}
```

---

## 🔍 Шаг 5: ДИАГНОСТИКА ПРОБЛЕМЫ С БОТОМ

Бот в статусе **"Restarting"** - он падает и перезапускается, создавая тонны логов!

```bash
# Смотрим последние логи бота (найти ошибку)
docker logs dieta-bot-1 --tail 200

# Смотрим логи в реальном времени
docker logs dieta-bot-1 -f

# Проверяем только ошибки
docker logs dieta-bot-1 2>&1 | grep -i error | tail -50

# Проверяем что API работает (бот может падать из-за недоступности API)
curl http://localhost:8000/health

# Проверяем переменные окружения бота
docker exec dieta-bot-1 env | grep -E "(BOT_TOKEN|API_BASE_URL|DATABASE)"
```

### Типичные причины падения бота:

#### 1. **API недоступен**
```bash
# Проверить API
docker-compose logs api --tail 50

# Перезапустить API
docker-compose restart api
```

#### 2. **Нет токена бота в .env**
```bash
# Проверить .env
cat .env | grep TG_TOKEN

# Если пусто - добавить
nano .env
# Добавить: TG_TOKEN=ваш_токен_от_BotFather

# Перезапустить бота
docker-compose restart bot
```

#### 3. **База данных недоступна**
```bash
# Проверить подключение к БД
cat .env | grep DATABASE_URL

# Тестовое подключение
docker exec dieta-bot-1 python -c "import asyncpg; print('OK')"
```

#### 4. **Конфликт токенов (TelegramConflictError)**
```bash
# Проверить что нет других процессов бота
ps aux | grep 'main.py' | grep -v grep

# Если есть - убить
sudo pkill -f "python.*main.py"

# Перезапустить контейнер
docker-compose restart bot
```

#### 5. **Недостаточно памяти**
```bash
# Проверить использование ресурсов
docker stats --no-stream

# Проверить память сервера
free -h
```

---

## ✅ Шаг 6: ПРОВЕРКА РЕЗУЛЬТАТОВ

```bash
# Проверить размер логов (должен быть < 100MB)
du -sh /var/lib/docker/containers/

# Проверить использование диска (должно освободиться место)
df -h /

# Проверить статус контейнеров (все должны быть Up, не Restarting!)
docker-compose ps

# Проверить что бот работает
docker logs dieta-bot-1 --tail 20

# Проверить настройки логирования
docker inspect dieta-bot-1 | grep -A 5 "LogConfig"
docker inspect dieta-frontend-1 | grep -A 5 "LogConfig"
```

### ✅ Ожидаемый результат:

```bash
CONTAINER ID   IMAGE              STATUS
122ada5cb082   dieta-frontend     Up 5 minutes   ✅
ad43f75183c3   dieta-bot          Up 5 minutes   ✅ (не Restarting!)

# Размер логов
/var/lib/docker/containers/  80M   (было: несколько GB)
```

---

## 📊 Шаг 7: МОНИТОРИНГ (для будущего)

### Создать скрипт мониторинга:
```bash
cd /opt/dieta

# Дать права на выполнение
chmod +x monitor_docker_disk.sh

# Запустить мониторинг
sudo bash monitor_docker_disk.sh
```

### Добавить в cron для автоматической очистки (каждую неделю):
```bash
# Открыть crontab
sudo crontab -e

# Добавить строку (очистка каждое воскресенье в 3:00)
0 3 * * 0 truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

---

## 🚨 БЫСТРЫЕ КОМАНДЫ (всё в одну строку)

### Очистка логов одной командой:
```bash
cd /opt/dieta && docker-compose stop && truncate -s 0 /var/lib/docker/containers/*/*-json.log && docker-compose up -d && docker-compose ps
```

### Полная очистка + обновление:
```bash
cd /opt/dieta && docker-compose down && docker system prune -a -f && git pull && docker-compose up -d --build && docker-compose ps
```

### Проверка статуса одной командой:
```bash
echo "=== ДИСК ===" && df -h / && echo "=== ЛОГИ ===" && du -sh /var/lib/docker/containers/ && echo "=== КОНТЕЙНЕРЫ ===" && docker-compose ps
```

---

## 🔧 ИСПРАВЛЕНИЕ ПАДАЮЩЕГО БОТА

Если после очистки бот всё ещё перезапускается:

```bash
# 1. Остановить бота
docker-compose stop bot

# 2. Проверить логи последнего падения
docker logs dieta-bot-1 --tail 500 > bot_error.log
cat bot_error.log | grep -i "error\|exception\|traceback" -A 5

# 3. Исправить проблему (зависит от ошибки):

# Если нет API:
docker-compose restart api && sleep 5 && docker-compose start bot

# Если нет токена:
nano .env  # Добавить TG_TOKEN
docker-compose up -d bot

# Если проблема с БД:
# Проверить DATABASE_URL в .env

# 4. Запустить бота заново
docker-compose up -d bot

# 5. Следить за логами
docker logs dieta-bot-1 -f
```

---

## 📞 ЕСЛИ ПРОБЛЕМА СОХРАНЯЕТСЯ

### Соберите диагностическую информацию:

```bash
cd /opt/dieta

# Создать отчет
echo "=== ДИСК ===" > diagnostic_report.txt
df -h / >> diagnostic_report.txt
echo "" >> diagnostic_report.txt

echo "=== ЛОГИ DOCKER ===" >> diagnostic_report.txt
du -sh /var/lib/docker/containers/*/ >> diagnostic_report.txt
echo "" >> diagnostic_report.txt

echo "=== КОНТЕЙНЕРЫ ===" >> diagnostic_report.txt
docker-compose ps >> diagnostic_report.txt
echo "" >> diagnostic_report.txt

echo "=== ЛОГИ БОТА ===" >> diagnostic_report.txt
docker logs dieta-bot-1 --tail 100 >> diagnostic_report.txt
echo "" >> diagnostic_report.txt

echo "=== НАСТРОЙКИ ЛОГИРОВАНИЯ ===" >> diagnostic_report.txt
docker inspect dieta-bot-1 | grep -A 10 "LogConfig" >> diagnostic_report.txt
docker inspect dieta-frontend-1 | grep -A 10 "LogConfig" >> diagnostic_report.txt

# Посмотреть отчет
cat diagnostic_report.txt
```

---

## 🎯 ИТОГО

### Что сделали:
1. ✅ Очистили логи Docker (освободили место)
2. ✅ Применили ограничения на размер логов (max 80MB)
3. ✅ Отключили избыточное логирование Nginx
4. ✅ Диагностировали проблему с падающим ботом
5. ✅ Настроили мониторинг

### Теперь логи:
- **Bot**: макс 30MB (было: бесконечно)
- **Frontend**: макс 10MB (было: несколько GB!)
- **API**: макс 30MB
- **Nginx**: макс 10MB

**Общий максимум: ~80MB вместо бесконечного роста!**

---

📅 **Проверьте панель управления Timeweb через час** - место должно освободиться!

