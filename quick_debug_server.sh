#!/bin/bash
echo "🔍 БЫСТРАЯ ДИАГНОСТИКА ПРОБЛЕМ НА СЕРВЕРЕ"
echo "========================================="

cd /opt/dieta || exit 1

echo "📊 1. Статус контейнеров:"
docker-compose ps

echo ""
echo "📋 2. Логи API (последние 50 строк):"
docker-compose logs --tail=50 api

echo ""
echo "📋 3. Логи Bot (последние 20 строк):"
docker-compose logs --tail=20 bot 2>/dev/null || echo "Bot контейнер не запущен"

echo ""
echo "📋 4. Проверка .env файла:"
echo "DATABASE_URL есть: $(grep -c 'DATABASE_URL=' .env)"
echo "TG_TOKEN есть: $(grep -c 'TG_TOKEN=' .env)"

echo ""
echo "🌐 5. Проверка сети:"
echo "Порт 8000: $(netstat -tlnp | grep :8000 || echo 'не занят')"
echo "Порт 3000: $(netstat -tlnp | grep :3000 || echo 'не занят')"

echo ""
echo "🔧 6. Попытка подключения к БД:"
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('DATABASE_URL загружен:', bool(os.getenv('DATABASE_URL')))
db_url = os.getenv('DATABASE_URL', '')
if 'postgresql' in db_url:
    print('Тип БД: PostgreSQL')
    if 'neondb' in db_url:
        print('Провайдер: Neon')
    print('URL длина:', len(db_url))
else:
    print('Тип БД: неизвестен')
" 2>/dev/null || echo "Python диагностика не удалась"

echo ""
echo "💾 7. Использование диска:"
df -h /opt/dieta

echo ""
echo "🧠 8. Использование памяти:"
free -h

echo ""
echo "📦 9. Docker информация:"
docker system df

echo ""
echo "🔧 10. БЫСТРЫЕ ИСПРАВЛЕНИЯ:"
echo "================================"
echo "Если API падает:"
echo "  docker-compose logs api | tail -20"
echo "  docker-compose restart api"
echo ""
echo "Если нужна полная перезагрузка:"
echo "  docker-compose down"
echo "  docker system prune -f"
echo "  docker-compose up -d"
echo ""
echo "Если проблемы с БД:"
echo "  Проверьте интернет-соединение до Neon"
echo "  ping ep-lively-hall-aduj1169-pooler.c-2.us-east-1.aws.neon.tech" 