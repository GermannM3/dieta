#!/bin/bash

echo "🔧 Установка зависимостей для диет-бота"
echo "========================================"

# Проверяем что venv активирован
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Виртуальное окружение не активировано!"
    echo "Активируйте venv: source venv/bin/activate"
    exit 1
fi

echo "✅ Виртуальное окружение активировано: $VIRTUAL_ENV"

# Обновляем pip
echo "📦 Обновление pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo "📦 Установка Python зависимостей..."
pip install -r requirements.txt

# Проверяем установку psutil
echo "🔍 Проверка psutil..."
python -c "import psutil; print(f'✅ psutil {psutil.__version__} установлен')"

# Устанавливаем nginx если его нет
if ! command -v nginx &> /dev/null; then
    echo "📦 Установка nginx..."
    apt update
    apt install -y nginx
else
    echo "✅ nginx уже установлен"
fi

# Устанавливаем node.js если его нет
if ! command -v node &> /dev/null; then
    echo "📦 Установка Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
else
    echo "✅ Node.js уже установлен: $(node --version)"
fi

# Устанавливаем npm зависимости для frontend
if [ -d "calorie-love-tracker" ]; then
    echo "📦 Установка npm зависимостей..."
    cd calorie-love-tracker
    npm install
    cd ..
else
    echo "⚠️  Папка calorie-love-tracker не найдена"
fi

echo "✅ Все зависимости установлены!"
echo "🚀 Теперь можно запускать: python start_all_services.py" 