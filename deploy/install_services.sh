#!/bin/bash
# Установка systemd-сервисов Dieta на сервере.
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/dieta}"
cd "$APP_DIR"

chmod +x scripts/auto_deploy.sh

cp -f api.service /etc/systemd/system/api.service
cp -f bot.service /etc/systemd/system/bot.service
cp -f deploy/dieta-deploy.service /etc/systemd/system/dieta-deploy.service
cp -f deploy/dieta-deploy.timer /etc/systemd/system/dieta-deploy.timer

cp -f deploy/warp-proxy.service /etc/systemd/system/warp-proxy.service
cp -f deploy/tg-healthcheck.service /etc/systemd/system/tg-healthcheck.service
cp -f deploy/tg-healthcheck.timer /etc/systemd/system/tg-healthcheck.timer
chmod +x scripts/tg_proxy_healthcheck.sh

systemctl daemon-reload

if command -v warp-cli >/dev/null 2>&1; then
    systemctl enable warp-proxy.service
    systemctl restart warp-proxy.service || true
fi

systemctl enable tg-healthcheck.timer
systemctl start tg-healthcheck.timer

systemctl enable api.service bot.service
systemctl enable dieta-deploy.timer
systemctl start dieta-deploy.timer

systemctl restart api.service
systemctl restart bot.service

echo "=== Status ==="
systemctl is-active api bot dieta-deploy.timer
systemctl list-timers dieta-deploy.timer --no-pager
