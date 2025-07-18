@echo off
REM Скрипт для запуска команд внутри контейнера API
REM Использование: run_in_container.bat <команда>

if "%1"=="" (
    echo Использование: %0 ^<команда^>
    echo.
    echo Примеры команд:
    echo   %0 "python create_admin.py create"
    echo   %0 "python setup_smtp.py test"
    echo   %0 "python setup_smtp.py examples"
    echo   %0 "python -c \"from api.email_service import EmailService; print(EmailService().is_configured)\""
    exit /b 1
)

set COMMAND=%*

echo 🚀 Запуск команды в контейнере API: %COMMAND%
echo ==================================================

REM Проверяем, запущен ли контейнер API
docker-compose ps api | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Контейнер API не запущен. Запускаем...
    docker-compose up -d api
    timeout /t 5 /nobreak >nul
)

REM Запускаем команду в контейнере
docker-compose exec api bash -c "%COMMAND%"

echo.
echo ✅ Команда выполнена 