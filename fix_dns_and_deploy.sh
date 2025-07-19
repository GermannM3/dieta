#!/bin/bash

echo "🔧 Исправление DNS и деплой проекта"
echo "=================================="

# 1. Исправляем DNS для Docker
echo "📡 Настройка DNS для Docker..."
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
EOF

# 2. Перезапускаем Docker
echo "🔄 Перезапуск Docker..."
sudo systemctl restart docker

# 3. Останавливаем все контейнеры
echo "🛑 Остановка контейнеров..."
docker-compose -f docker-compose.fresh.yml down

# 4. Очищаем образы
echo "🧹 Очистка образов..."
docker rmi dieta_api:latest dieta_bot:latest dieta_frontend:latest dieta_nginx:latest 2>/dev/null || true
docker system prune -f

# 5. Пересобираем с нуля
echo "🔨 Пересборка проекта..."
docker-compose -f docker-compose.fresh.yml build --no-cache

# 6. Запускаем
echo "🚀 Запуск проекта..."
docker-compose -f docker-compose.fresh.yml up -d

# 7. Ждем запуска
echo "⏳ Ожидание запуска..."
sleep 10

# 8. Проверяем статус
echo "📊 Статус контейнеров:"
docker-compose -f docker-compose.fresh.yml ps

# 9. Проверяем API
echo "🔍 Проверка API..."
curl -s http://localhost/api/health || echo "API еще не готов"

# 10. Исправляем админа
echo "👤 Исправление админа..."
docker exec -it dieta_api_1 python fix_admin_complete.py

echo "✅ Готово! Проверьте сайт: http://5.129.198.80/" 