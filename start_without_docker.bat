@echo off
echo ========================================
echo   Запуск Диетолог Бота БЕЗ Docker
echo ========================================
echo.

:: Проверка .env файла
if not exist .env (
    echo ERROR: Файл .env не найден!
    echo Создайте .env файл из env.example
    pause
    exit /b 1
)

:: Запуск API сервера
echo [1/3] Запуск API сервера...
start "API Server" cmd /k "python improved_api_server.py"
timeout /t 3 /nobreak > nul

:: Запуск Telegram бота
echo [2/3] Запуск Telegram бота...
start "Telegram Bot" cmd /k "python main.py"
timeout /t 2 /nobreak > nul

:: Запуск React фронтенда
echo [3/3] Запуск React фронтенда...
cd calorie-love-tracker
start "React Frontend" cmd /k "npm install && npm run dev"
cd ..

echo.
echo ========================================
echo   Все сервисы запущены!
echo ========================================
echo.
echo Доступные сервисы:
echo - API Server: http://localhost:8000
echo - API Docs: http://localhost:8000/docs  
echo - Frontend: http://localhost:5173
echo - Telegram Bot: @tvoy_diet_bot
echo.
echo Для остановки закройте все окна CMD
echo.
pause 