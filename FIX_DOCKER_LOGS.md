# 🚨 ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С ЛОГАМИ DOCKER

## 📊 Проблема

Docker контейнеры (особенно фронтенд и бот) накапливают логи без ограничений и **захламляют диск**.

### Что было изменено:

1. ✅ **docker-compose.yml** - добавлены ограничения на размер логов
2. ✅ **nginx-frontend.conf** - отключены access логи (только ошибки)
3. ✅ **cleanup_docker_logs.sh** - скрипт для очистки существующих логов

---

## ⚡ БЫСТРОЕ ИСПРАВЛЕНИЕ

### Шаг 1: Очистить существующие логи

```bash
# Дать права на выполнение скрипта
chmod +x cleanup_docker_logs.sh

# Запустить очистку
sudo bash cleanup_docker_logs.sh
```

Скрипт:
- Покажет текущий размер логов
- Остановит контейнеры
- Очистит все логи
- Запустит контейнеры с новыми настройками

### Шаг 2: Проверить размер логов

```bash
# Проверить размер логов Docker
sudo du -sh /var/lib/docker/containers/*/

# Общий размер
sudo du -sh /var/lib/docker/containers/
```

### Шаг 3: Применить изменения

```bash
# Перезапустить контейнеры с новыми настройками
docker-compose down
docker-compose up -d

# Проверить статус
docker-compose ps
```

---

## 📝 ЧТО ИЗМЕНЕНО

### 1. docker-compose.yml - ограничения на логи

Добавлено для всех сервисов:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"    # Максимальный размер одного файла лога
    max-file: "3"      # Количество файлов для ротации
```

**Результат:**
- **Bot**: макс 10MB x 3 файла = **30MB**
- **API**: макс 10MB x 3 файла = **30MB**  
- **Frontend**: макс 5MB x 2 файла = **10MB**
- **Nginx**: макс 5MB x 2 файла = **10MB**

**Общий максимум логов: ~80MB** (вместо бесконечного роста)

### 2. nginx-frontend.conf - оптимизация логирования

```nginx
# Отключены access логи (каждый запрос к файлам)
access_log off;

# Логируем только ошибки
error_log /var/log/nginx/error.log error;
```

---

## 🔍 ДИАГНОСТИКА ПРОБЛЕМЫ С БОТОМ

Бот находится в состоянии **"Restarting (1)"** - это значит он **падает и перезапускается**.

### Проверить логи бота:

```bash
# Посмотреть последние логи бота
docker logs dieta-bot-1 --tail 100

# Следить за логами в реальном времени
docker logs dieta-bot-1 -f

# Проверить последние 50 строк с ошибками
docker logs dieta-bot-1 --tail 50 2>&1 | grep -i error
```

### Типичные причины падения бота:

1. **Ошибка подключения к API**
   ```bash
   # Проверить что API работает
   curl http://localhost:8000/health
   ```

2. **Нет переменных окружения**
   ```bash
   # Проверить .env файл
   cat .env | grep -E "(BOT_TOKEN|API_BASE_URL)"
   ```

3. **База данных недоступна**
   ```bash
   # Проверить что база данных работает
   docker exec dieta-bot-1 python -c "import sqlite3; print('DB OK')"
   ```

4. **Redis недоступен** (если используется)
   ```bash
   # Проверить логи на ошибки Redis
   docker logs dieta-bot-1 2>&1 | grep -i redis
   ```

5. **Конфликт с другим ботом** (TelegramConflictError)
   ```bash
   # Проверить что нет других процессов бота
   ps aux | grep 'main.py' | grep -v grep
   ```

### Исправить проблему с ботом:

```bash
# 1. Остановить бота
docker-compose stop bot

# 2. Проверить и исправить .env
nano .env

# 3. Пересобрать и запустить
docker-compose up -d --build bot

# 4. Проверить логи
docker logs dieta-bot-1 -f
```

---

## 📊 МОНИТОРИНГ ЛОГОВ

### Ежедневная проверка размера логов:

```bash
# Создать alias для быстрой проверки
echo 'alias docker-logs-size="sudo du -sh /var/lib/docker/containers/*/"' >> ~/.bashrc
source ~/.bashrc

# Теперь можно просто:
docker-logs-size
```

### Автоматическая очистка старых логов (cron):

```bash
# Добавить в crontab
sudo crontab -e

# Добавить строку (очистка каждую неделю в воскресенье 3:00):
0 3 * * 0 /usr/bin/docker system prune -f --volumes > /dev/null 2>&1
```

---

## ✅ ПРОВЕРКА РЕЗУЛЬТАТОВ

После применения всех исправлений:

```bash
# 1. Проверить размер логов (должен быть < 100MB)
sudo du -sh /var/lib/docker/containers/

# 2. Проверить статус контейнеров (все должны быть Up)
docker-compose ps

# 3. Проверить логи бота (не должно быть ошибок)
docker logs dieta-bot-1 --tail 50

# 4. Проверить место на диске
df -h /
```

### Ожидаемый результат:

```
CONTAINER ID   IMAGE              STATUS
122ada5cb082   dieta-frontend     Up 2 minutes
ad43f75183c3   dieta-bot          Up 2 minutes   ✅ (не Restarting!)
```

---

## 🔧 ДОПОЛНИТЕЛЬНЫЕ КОМАНДЫ

### Очистить всю систему Docker:

```bash
# ⚠️ ВНИМАНИЕ: Удалит все неиспользуемые данные!
docker system prune -a --volumes

# Показать что будет очищено (без удаления)
docker system df
```

### Экспорт логов перед очисткой:

```bash
# Сохранить логи перед очисткой
mkdir -p ~/docker-logs-backup
docker logs dieta-bot-1 > ~/docker-logs-backup/bot-$(date +%Y%m%d).log
docker logs dieta-frontend > ~/docker-logs-backup/frontend-$(date +%Y%m%d).log
```

---

## 📞 ЕСЛИ ПРОБЛЕМА СОХРАНЯЕТСЯ

1. **Проверить реальную причину**: `docker logs dieta-bot-1 --tail 200`
2. **Проверить ресурсы сервера**: `free -h` и `df -h`
3. **Проверить переменные окружения**: `docker exec dieta-bot-1 env`
4. **Перезапустить всё**: `docker-compose down && docker-compose up -d --build`

Если бот продолжает падать - отправьте вывод команды:
```bash
docker logs dieta-bot-1 --tail 100 > bot_error.log
cat bot_error.log
```

