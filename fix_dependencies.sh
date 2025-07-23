#!/bin/bash

# Скрипт для принудительного разрешения конфликтов зависимостей
# Использование: ./fix_dependencies.sh

set -e

echo "🔧 Исправляем конфликты зависимостей..."

# Активируем виртуальное окружение
source venv/bin/activate

# Очищаем все кеши
echo "🧹 Очищаем кеши..."
pip cache purge || true
pip uninstall -y aiogram fastapi mistralai pydantic || true

# Обновляем pip
echo "📦 Обновляем pip..."
pip install --upgrade pip

# Устанавливаем зависимости по одной, начиная с базовых
echo "📥 Устанавливаем базовые зависимости..."
pip install --no-cache-dir pydantic>=2.10.3
pip install --no-cache-dir fastapi>=0.115,<0.120
pip install --no-cache-dir aiogram>=3.4,<4
pip install --no-cache-dir mistralai>=1.9,<2

# Устанавливаем остальные зависимости
echo "📥 Устанавливаем остальные зависимости..."
pip install --no-cache-dir -r requirements.txt

echo "✅ Зависимости исправлены!"
echo "🔍 Проверяем установленные версии..."
pip list | grep -E "(aiogram|fastapi|mistralai|pydantic)" 