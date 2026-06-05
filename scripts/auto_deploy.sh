#!/bin/bash
# Автодеплой: подтягивает main с GitHub и перезапускает сервисы при новом коммите.
set -euo pipefail

APP_DIR="${APP_DIR:-/opt/dieta}"
BRANCH="${DEPLOY_BRANCH:-main}"
LOG_TAG="dieta-deploy"

cd "$APP_DIR"

if [[ ! -d .git ]]; then
    logger -t "$LOG_TAG" "ERROR: $APP_DIR is not a git repo"
    exit 1
fi

git fetch origin "$BRANCH" --quiet

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "origin/$BRANCH")

if [[ "$LOCAL" == "$REMOTE" ]]; then
    exit 0
fi

logger -t "$LOG_TAG" "New commit $REMOTE (was $LOCAL), deploying..."

git pull origin "$BRANCH" --ff-only

if [[ -f venv/bin/activate ]]; then
    # shellcheck disable=SC1091
    source venv/bin/activate
    pip install -q -r requirements.txt
fi

systemctl restart api.service
systemctl restart bot.service

logger -t "$LOG_TAG" "Deployed $REMOTE successfully"
