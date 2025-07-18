#!/bin/bash

# Скрипт для запуска команд внутри контейнера API
# Использование: ./run_in_container.sh <команда>

if [ $# -eq 0 ]; then
    echo "Использование: $0 <команда>"
    echo ""
    echo "Примеры команд:"
    echo "  $0 'python create_admin.py create'"
    echo "  $0 'python setup_smtp.py test'"
    echo "  $0 'python setup_smtp.py examples'"
    echo "  $0 'python -c \"from api.email_service import EmailService; print(EmailService().is_configured)\"'"
    exit 1
fi

COMMAND="$1"

echo "🚀 Запуск команды в контейнере API: $COMMAND"
echo "=================================================="

# Проверяем, запущен ли контейнер API
if ! docker-compose ps api | grep -q "Up"; then
    echo "❌ Контейнер API не запущен. Запускаем..."
    docker-compose up -d api
    sleep 5
fi

# Запускаем команду в контейнере
docker-compose exec api bash -c "$COMMAND"

echo ""
echo "✅ Команда выполнена" 