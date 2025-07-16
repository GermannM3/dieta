@echo off
echo ===============================================
echo     ДЕПЛОЙ ВЕБ-ПРИЛОЖЕНИЯ НА TIMEWEB CLOUD
echo ===============================================
echo.

echo [1/8] Подключение к серверу...
scp -r calorie-love-tracker/* root@5.129.198.80:/tmp/webapp-deploy/
if %ERRORLEVEL% neq 0 (
    echo ОШИБКА: Не удалось скопировать файлы на сервер
    pause
    exit /b 1
)

echo [2/8] Выполнение команд на сервере...
ssh root@5.129.198.80 "
echo '=== Остановка существующего контейнера ==='
docker stop diet-webapp 2>/dev/null || true
docker rm diet-webapp 2>/dev/null || true

echo '=== Создание директории и копирование файлов ==='
mkdir -p /opt/diet-webapp
cp -r /tmp/webapp-deploy/* /opt/diet-webapp/
cd /opt/diet-webapp

echo '=== Сборка Docker образа ==='
docker build -t diet-webapp:latest \
  --build-arg VITE_API_URL=http://5.129.198.80:8000 \
  --build-arg VITE_APP_TITLE='Твой Диетолог - Персональный ИИ-помощник' \
  --build-arg VITE_APP_DESCRIPTION='Продвинутый телеграм-бот с личным диетологом' \
  --build-arg VITE_TELEGRAM_BOT_USERNAME=@tvoy_diet_bot \
  .

echo '=== Запуск контейнера с переменными окружения ==='
docker run -d \
  --name diet-webapp \
  --restart unless-stopped \
  -p 3000:3000 \
  -e VITE_API_URL=http://5.129.198.80:8000 \
  -e VITE_APP_TITLE='Твой Диетолог - Персональный ИИ-помощник' \
  -e VITE_APP_DESCRIPTION='Продвинутый телеграм-бот с личным диетологом' \
  -e VITE_TELEGRAM_BOT_USERNAME=@tvoy_diet_bot \
  -e PORT=3000 \
  diet-webapp:latest

echo '=== Настройка nginx проксирования ==='
cat > /etc/nginx/sites-available/webapp << 'EOL'
server {
    listen 80;
    server_name 5.129.198.80;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOL

ln -sf /etc/nginx/sites-available/webapp /etc/nginx/sites-enabled/webapp
nginx -t && systemctl reload nginx

echo '=== Очистка временных файлов ==='
rm -rf /tmp/webapp-deploy

echo '=== Проверка статуса ==='
docker ps | grep diet-webapp
"

if %ERRORLEVEL% neq 0 (
    echo ОШИБКА: Не удалось выполнить команды на сервере
    pause
    exit /b 1
)

echo.
echo ===============================================
echo           ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!
echo ===============================================
echo.
echo Веб-приложение доступно по адресу:
echo http://5.129.198.80
echo.
echo Для проверки логов выполните:
echo ssh root@5.129.198.80 "docker logs diet-webapp"
echo.
pause 