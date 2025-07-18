@echo off
echo ========================================
echo 🚀 Деплой с обновленной конфигурацией домена
echo ========================================

echo.
echo 📝 Коммит изменений...
git add .
git commit -m "Обновлена конфигурация nginx для доменов твой-калькулятор.рф и tvoi-kalkulyator.ru"

echo.
echo 📤 Пуш в репозиторий...
git push

echo.
echo 🐳 Остановка контейнеров...
docker-compose down

echo.
echo 🔨 Пересборка контейнеров...
docker-compose up --build -d

echo.
echo ⏳ Ожидание запуска контейнеров...
timeout /t 10 /nobreak >nul

echo.
echo 📊 Статус контейнеров:
docker-compose ps

echo.
echo 🔍 Проверка логов API:
docker-compose logs api --tail=10

echo.
echo 🔍 Проверка логов фронтенда:
docker-compose logs frontend --tail=10

echo.
echo ✅ Деплой завершен!
echo 🌐 Домены должны работать:
echo    - http://твой-калькулятор.рф
echo    - http://tvoi-kalkulyator.ru
echo.
echo 📧 Для настройки SMTP выполните:
echo    python setup_smtp.py examples
echo.
echo 👤 Для создания администратора выполните:
echo    python create_admin.py create 