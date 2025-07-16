Write-Host "===============================================" -ForegroundColor Green
Write-Host "     ДЕПЛОЙ ВЕБ-ПРИЛОЖЕНИЯ НА TIMEWEB CLOUD" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

$serverIP = "5.129.198.80"
$serverUser = "root"

Write-Host "[1/8] Подготовка файлов..." -ForegroundColor Yellow

# Создаем временную директорию для деплоя
$tempDir = "webapp-deploy-temp"
if (Test-Path $tempDir) {
    Remove-Item -Recurse -Force $tempDir
}
New-Item -ItemType Directory -Path $tempDir | Out-Null

# Копируем файлы веб-приложения
Copy-Item -Recurse -Path "calorie-love-tracker\*" -Destination $tempDir

Write-Host "[2/8] Копирование файлов на сервер..." -ForegroundColor Yellow

# Используем scp для копирования
$scpResult = Start-Process -FilePath "scp" -ArgumentList "-r", "$tempDir\*", "$serverUser@$serverIP" -Wait -PassThru -NoNewWindow
if ($scpResult.ExitCode -ne 0) {
    Write-Host "ОШИБКА: Не удалось скопировать файлы на сервер" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "[3/8] Выполнение команд деплоя на сервере..." -ForegroundColor Yellow

# SSH команды для деплоя
$sshCommands = @"
echo '=== Остановка существующего контейнера ==='
docker stop diet-webapp 2>/dev/null || true
docker rm diet-webapp 2>/dev/null || true

echo '=== Создание директории и копирование файлов ==='
mkdir -p /opt/diet-webapp
cp -r /home/root/* /opt/diet-webapp/ 2>/dev/null || true
cd /opt/diet-webapp

echo '=== Сборка Docker образа ==='
docker build -t diet-webapp:latest \
  --build-arg VITE_API_URL=http://5.129.198.80:8000 \
  --build-arg VITE_APP_TITLE='Твой Диетолог - Персональный ИИ-помощник' \
  --build-arg VITE_APP_DESCRIPTION='Продвинутый телеграм-бот с личным диетологом' \
  --build-arg VITE_TELEGRAM_BOT_USERNAME=@tvoy_diet_bot \
  .

echo '=== Запуск контейнера ==='
docker run -d \
  --name diet-webapp \
  --restart unless-stopped \
  -p 3000:3000 \
  diet-webapp:latest

echo '=== Настройка nginx ==='
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

echo '=== Проверка статуса ==='
docker ps | grep diet-webapp
"@

$sshResult = Start-Process -FilePath "ssh" -ArgumentList "$serverUser@$serverIP", "`"$sshCommands`"" -Wait -PassThru -NoNewWindow
if ($sshResult.ExitCode -ne 0) {
    Write-Host "ОШИБКА: Не удалось выполнить команды на сервере" -ForegroundColor Red
    Read-Host "Нажмите Enter для выхода"
    exit 1
}

Write-Host "[4/8] Очистка временных файлов..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $tempDir

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "           ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Веб-приложение доступно по адресу:" -ForegroundColor Cyan
Write-Host "http://5.129.198.80" -ForegroundColor White
Write-Host ""
Write-Host "Для проверки логов выполните:" -ForegroundColor Cyan
Write-Host "ssh root@5.129.198.80 `"docker logs diet-webapp`"" -ForegroundColor White
Write-Host ""
Read-Host "Нажмите Enter для выхода" 