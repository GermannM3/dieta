#!/bin/bash
# Проверяет доступ к Telegram через WARP и перезапускает прокси/бот при сбое.
set -euo pipefail

LOG_TAG="tg-healthcheck"
PROXY="socks5://127.0.0.1:40000"

if curl -sf --connect-timeout 10 --proxy "$PROXY" "https://api.telegram.org" >/dev/null; then
    exit 0
fi

logger -t "$LOG_TAG" "Telegram unreachable via WARP, restarting warp-svc, warp-proxy, bot"

systemctl restart warp-svc
sleep 4
warp-cli --accept-tos mode proxy 2>/dev/null || true
warp-cli --accept-tos connect 2>/dev/null || true
sleep 3
systemctl restart warp-proxy bot

logger -t "$LOG_TAG" "Restart complete"
