#!/bin/bash

# Скрипт для мониторинга использования диска Docker контейнерами

echo "🔍 МОНИТОРИНГ DOCKER ДИСКОВОГО ПРОСТРАНСТВА"
echo "==========================================="
echo ""

# Проверка прав sudo
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Пожалуйста, запустите скрипт с sudo:"
    echo "   sudo bash monitor_docker_disk.sh"
    exit 1
fi

# Общая информация о диске
echo "💾 ИСПОЛЬЗОВАНИЕ ДИСКА:"
df -h / | tail -n 1
echo ""

# Docker система в целом
echo "🐳 DOCKER СИСТЕМА:"
docker system df
echo ""

# Размер контейнеров
echo "📦 РАЗМЕР КОНТЕЙНЕРОВ:"
docker ps -a --size --format "table {{.Names}}\t{{.Status}}\t{{.Size}}" | head -n 10
echo ""

# Размер логов каждого контейнера
echo "📝 РАЗМЕР ЛОГОВ КОНТЕЙНЕРОВ:"
for container in /var/lib/docker/containers/*/; do
    container_id=$(basename "$container")
    container_name=$(docker ps -a --filter "id=${container_id:0:12}" --format "{{.Names}}" 2>/dev/null)
    
    if [ -n "$container_name" ]; then
        log_file="$container/${container_id}-json.log"
        if [ -f "$log_file" ]; then
            size=$(du -h "$log_file" | cut -f1)
            status=$(docker ps -a --filter "id=${container_id:0:12}" --format "{{.Status}}")
            echo "  📄 $container_name: $size (${status:0:30})"
        fi
    fi
done
echo ""

# Топ 10 самых больших образов
echo "🖼️  ТОП-10 БОЛЬШИХ ОБРАЗОВ:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | head -n 11
echo ""

# Неиспользуемые данные
echo "🗑️  НЕИСПОЛЬЗУЕМЫЕ ДАННЫЕ (можно очистить):"
docker system df -v | grep -A 10 "Reclaimable"
echo ""

# Предупреждения
DISK_USAGE=$(df / | tail -n 1 | awk '{print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️  ВНИМАНИЕ: Использование диска > 80%!"
    echo ""
    echo "Рекомендуемые действия:"
    echo "1. Очистить логи: sudo bash cleanup_docker_logs.sh"
    echo "2. Удалить неиспользуемые данные: docker system prune -a"
    echo "3. Проверить логи контейнеров: docker logs <container_name>"
    echo ""
elif [ "$DISK_USAGE" -gt 90 ]; then
    echo "🚨 КРИТИЧНО: Использование диска > 90%!"
    echo ""
    echo "СРОЧНО выполните:"
    echo "1. sudo bash cleanup_docker_logs.sh"
    echo "2. docker system prune -a --volumes"
    echo ""
else
    echo "✅ Использование диска в норме ($DISK_USAGE%)"
    echo ""
fi

# Проверка настроек логирования
echo "⚙️  ПРОВЕРКА НАСТРОЕК ЛОГИРОВАНИЯ:"
for container in $(docker ps --format "{{.Names}}"); do
    log_config=$(docker inspect "$container" | grep -A 5 "LogConfig" | grep -E "(Type|max-size|max-file)" | tr -d ' ",')
    echo "  📦 $container:"
    echo "    $log_config" | sed 's/^/    /'
done
echo ""

echo "📊 РЕКОМЕНДАЦИИ:"
echo "  - Логи должны иметь max-size и max-file"
echo "  - Регулярно запускайте: docker system prune -f"
echo "  - Мониторьте размер логов: du -sh /var/lib/docker/containers/*/"
echo ""

