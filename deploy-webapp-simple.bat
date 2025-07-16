@echo off
echo ===============================================
echo     DEPLOY WEB-APP TO TIMEWEB CLOUD
echo ===============================================
echo.

echo [1/3] Copying files to server...
scp -r calorie-love-tracker root@5.129.198.80:/tmp/webapp-deploy
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to copy files to server
    pause
    exit /b 1
)

echo [2/3] Building and starting container...
ssh root@5.129.198.80 "cd /tmp/webapp-deploy && docker stop diet-webapp 2>/dev/null || true && docker rm diet-webapp 2>/dev/null || true && mkdir -p /opt/diet-webapp && cp -r * /opt/diet-webapp/ && cd /opt/diet-webapp && docker build -t diet-webapp:latest --build-arg VITE_API_URL=http://5.129.198.80:8000 --build-arg VITE_APP_TITLE='Your Dietolog - AI Assistant' --build-arg VITE_APP_DESCRIPTION='Advanced telegram bot with personal dietitian' --build-arg VITE_TELEGRAM_BOT_USERNAME=@tvoy_diet_bot . && docker run -d --name diet-webapp --restart unless-stopped -p 3000:3000 diet-webapp:latest"

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to deploy on server
    pause
    exit /b 1
)

echo [3/3] Setting up nginx...
ssh root@5.129.198.80 "echo 'server { listen 80; server_name 5.129.198.80; location / { proxy_pass http://localhost:3000; proxy_set_header Host \$host; proxy_set_header X-Real-IP \$remote_addr; proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for; proxy_set_header X-Forwarded-Proto \$scheme; } }' > /etc/nginx/sites-available/webapp && ln -sf /etc/nginx/sites-available/webapp /etc/nginx/sites-enabled/webapp && nginx -t && systemctl reload nginx && rm -rf /tmp/webapp-deploy"

echo.
echo ===============================================
echo           DEPLOYMENT COMPLETED!
echo ===============================================
echo.
echo Web app is available at:
echo http://5.129.198.80
echo.
echo To check logs run:
echo ssh root@5.129.198.80 "docker logs diet-webapp"
echo.
pause 