# Исправление проблем на сервере Timeweb

## Проблема: Файлы не находятся, docker-compose не запускается

### Шаг 1: Правильная навигация по файлам
```bash
# Подключение к серверу
ssh root@5.129.198.80

# Переход в правильную папку (вы клонировали в /opt/dieta/dieta)
cd /opt/dieta/dieta

# Проверим что файлы есть
ls -la

# Должны увидеть: docker-compose.yml, auto-deploy.sh, main.py, etc.
```

### Шаг 2: Установка прав и запуск
```bash
# Даем права на выполнение
chmod +x auto-deploy.sh

# Запускаем скрипт деплоя
./auto-deploy.sh
```

### Шаг 3: Если docker-compose не найден
```bash
# Проверим наличие файла
ls -la docker-compose.yml

# Если файла нет, скачаем актуальную версию
curl -O https://raw.githubusercontent.com/GermannM3/dieta/main/docker-compose.yml
```

### Шаг 4: Настройка .env файла
```bash
# Создаем или редактируем .env
nano .env

# Добавляем переменные:
TG_TOKEN=ваш_токен_бота
DATABASE_URL=postgresql://username:password@host:port/database
MISTRAL_API_KEY=ваш_ключ_mistral
GIGACHAT_CLIENT_SECRET=ваш_ключ_gigachat
GIGACHAT_CLIENT_ID=ваш_id_gigachat
API_BASE_URL=http://5.129.198.80:8000
```

### Шаг 5: Проверка Docker
```bash
# Проверим установлен ли Docker
docker --version
docker-compose --version

# Если не установлен, устанавливаем
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Шаг 6: Запуск сервисов
```bash
# Из папки /opt/dieta/dieta
docker-compose up --build -d

# Проверим статус
docker-compose ps

# Смотрим логи
docker-compose logs -f
```

### Альтернативный путь через Python
```bash
# Установка зависимостей Python
python3 -m pip install -r requirements.txt

# Активация виртуального окружения (если нужно)
python3 -m venv venv
source venv/bin/activate

# Запуск сервисов
python3 start_all_services.py
```

## Диагностика проблем

### Проверка структуры папок
```bash
pwd  # должно показать /opt/dieta/dieta
ls -la  # должны видеть все файлы проекта
```

### Проверка git репозитория
```bash
git status
git pull origin main  # обновление до последней версии
```

### Если команды не работают
```bash
# Проверим PATH
echo $PATH

# Найдем где установлен docker-compose
which docker-compose
find / -name docker-compose 2>/dev/null
``` 