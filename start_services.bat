@echo off
chcp 65001 >nul
echo 🤖 Запуск всех сервисов диет-бота
echo =================================

echo 🔧 Проверка зависимостей...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python найден

echo 🚀 Запуск всех сервисов...
python start_all_services.py

echo.
echo ✅ Все сервисы запущены!
echo 📱 Бот: @tvoy_diet_bot
echo 🌐 Сайт: http://5.129.198.80
echo 📊 API: http://5.129.198.80:8000/docs
echo 💎 Премиум функции:
echo    • Распознавание еды на фото
echo    • Индивидуальный план питания
echo.
pause 