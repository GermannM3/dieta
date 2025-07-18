@echo off
echo ================================================
echo     ПОЛНЫЙ ДЕПЛОЙ НА СЕРВЕР
echo ================================================
echo.

echo [1/5] Проверка статуса Git...
git status

echo.
echo [2/5] Добавление всех изменений...
git add .

echo.
echo [3/5] Создание коммита...
git commit -m "Исправления: трекер воды, жировая масса в профиле, админ-панель"

echo.
echo [4/5] Пуш в GitHub...
git push origin main

echo.
echo [5/5] Деплой на сервер...
ssh root@5.129.198.80 "cd /opt/dieta && git pull origin main && docker-compose down && docker-compose build --no-cache && docker-compose up -d"

echo.
echo ================================================
echo           ДЕПЛОЙ ЗАВЕРШЕН!
echo ================================================
echo.
echo Что было исправлено:
echo ✅ Трекер воды - теперь добавляет воду в локальную БД
echo ✅ Жировая масса - отображается в профиле пользователя
echo ✅ Админ-панель - создана для управления пользователями
echo ✅ Администратор - создан (germannm@vk.com / Germ@nnM3)
echo ✅ Поля БД - добавлены is_premium, body_fat_percent, goal_fat_percent
echo.
echo Веб-приложение: http://5.129.198.80
echo API сервер: http://5.129.198.80:8000
echo.
pause 