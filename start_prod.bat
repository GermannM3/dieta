@echo off
echo 🚀 Запуск продакшен версии с nginx на порту 80...

REM Остановить все контейнеры
echo 🛑 Остановка существующих контейнеров...
docker-compose down

REM Удалить старые образы (опционально)
echo 🧹 Очистка старых образов...
docker system prune -f

REM Запустить продакшен версию
echo 🏗️ Сборка и запуск продакшен контейнеров...
docker-compose -f docker-compose.prod.yml up --build -d

REM Показать статус
echo 📊 Статус контейнеров:
docker-compose -f docker-compose.prod.yml ps

echo ✅ Продакшен версия запущена!
echo 🌐 Сайт доступен по адресу: http://5.129.198.80
echo 📱 API доступен по адресу: http://5.129.198.80/api
echo 📚 Документация API: http://5.129.198.80/docs

pause 