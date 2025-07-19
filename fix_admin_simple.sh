#!/bin/bash

echo "🔧 Исправление админа через временный контейнер"
echo "==============================================="

# 1. Проверим что контейнеры запущены
echo "🔍 Проверка контейнеров..."
docker-compose -f docker-compose.fresh.yml ps

# 2. Попробуем подключиться к API контейнеру
echo "🔗 Подключение к API контейнеру..."
if docker exec -it dieta-api-1 python --version 2>/dev/null; then
    echo "✅ Подключение к контейнеру работает"
    docker exec -it dieta-api-1 python fix_admin_complete.py
else
    echo "❌ Не удалось подключиться к контейнеру"
    echo "🔧 Попробуем через временный контейнер..."
    
    # Создаем временный контейнер с теми же настройками
    docker run --rm -it \
        --network dieta_app-network \
        -v $(pwd):/app \
        -w /app \
        --env-file .env \
        dieta-api \
        python fix_admin_complete.py
fi

echo "✅ Исправление админа завершено!"
echo "🔐 Данные для входа:"
echo "   Email: germannm@vk.com"
echo "   Пароль: admin123" 