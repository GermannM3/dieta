@echo off
chcp 65001 >nul
echo 🛑 Остановка всех сервисов диет-бота
echo ===================================

echo 🔌 Остановка процессов...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im npm.exe >nul 2>&1
taskkill /f /im nginx.exe >nul 2>&1

echo ✅ Все сервисы остановлены!
pause 