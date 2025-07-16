@echo off
chcp 65001 >nul
echo 🚀 Быстрый деплой Диетолог-бота
echo ================================

echo.
echo 🔍 Проверка системы...
python quick_fix_deploy.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Проверка не пройдена!
    echo 💡 Исправьте ошибки и попробуйте снова
    pause
    exit /b 1
)

echo.
echo ✅ Система готова!
echo 🚀 Запуск всех сервисов...
echo.

python start_all_services.py

echo.
echo 🛑 Сервисы остановлены
pause 