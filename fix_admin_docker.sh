#!/bin/bash

echo "🔧 Исправляем админа через Docker..."

cd /opt/dieta

# Исправляем админа через правильный синтаксис Docker
docker run --rm -it \
  -v $(pwd):/app \
  -w /app \
  --env-file .env \
  dieta-api \
  python fix_admin_complete.py

echo "✅ Админ исправлен!" 