@echo off
echo Останавливаю все сервисы...
echo.

:: Останавливаем Python процессы
taskkill /F /IM python.exe 2>nul
if %errorlevel% == 0 (
    echo [OK] Python процессы остановлены
) else (
    echo [INFO] Python процессы не найдены
)

:: Останавливаем Node процессы
taskkill /F /IM node.exe 2>nul
if %errorlevel% == 0 (
    echo [OK] Node процессы остановлены
) else (
    echo [INFO] Node процессы не найдены
)

echo.
echo Все сервисы остановлены!
pause 