#!/bin/bash

echo "🧹 ОЧИСТКА DOCKER ЛОГОВ"
echo "=========================="
echo ""

# Проверка прав sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Пожалуйста, запустите скрипт с sudo:"
    echo "   sudo bash cleanup_docker_logs.sh"
    exit 1
fi

# Показываем текущий размер логов
echo "📊 Текущий размер логов Docker:"
du -sh /var/lib/docker/containers/*/
echo ""

# Получаем общий размер
TOTAL_SIZE=$(du -sh /var/lib/docker/containers/ | cut -f1)
echo "📦 Общий размер: $TOTAL_SIZE"
echo ""

# Спрашиваем подтверждение
read -p "⚠️  Очистить все логи контейнеров? (yes/no): " -r
echo ""
if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
    echo "❌ Отменено"
    exit 1
fi

# Останавливаем контейнеры
echo "⏸️  Останавливаем контейнеры..."
docker-compose stop

# Очищаем логи
echo "🗑️  Очищаем логи..."
truncate -s 0 /var/lib/docker/containers/*/*-json.log

# Показываем новый размер
echo ""
echo "✅ Логи очищены!"
echo "📊 Новый размер:"
du -sh /var/lib/docker/containers/*/
echo ""

NEW_SIZE=$(du -sh /var/lib/docker/containers/ | cut -f1)
echo "📦 Общий размер: $NEW_SIZE"
echo ""

# Запускаем контейнеры обратно
echo "▶️  Запускаем контейнеры с новыми настройками логирования..."
docker-compose up -d

echo ""
echo "✅ ГОТОВО!"
echo ""
echo "📝 Теперь логи ограничены:"
echo "   - Bot/API: макс 10MB x 3 файла = 30MB"
echo "   - Frontend/Nginx: макс 5MB x 2 файла = 10MB"
echo ""
echo "📊 Проверить размер логов можно командой:"
echo "   sudo du -sh /var/lib/docker/containers/*/"

