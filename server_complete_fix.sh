#!/bin/bash
echo "🔧 Исчерпывающее исправление проблем на сервере Timeweb"
echo "======================================================="

# Переходим в правильную папку
echo "📂 Переход в папку /opt/dieta..."
cd /opt/dieta || { echo "❌ Папка /opt/dieta не найдена!"; exit 1; }

echo "📍 Текущая папка: $(pwd)"

# Принудительно обновляем проект
echo "🔄 Принудительное обновление проекта..."
git fetch origin
git reset --hard origin/main
git pull origin main

# Исправляем проблему с импортом в PresetPicker.jsx
echo "🔧 Исправление импорта в PresetPicker.jsx..."
sed -i "s|import { getFoodCalories, searchFood } from '../lib/foodData';|import { getFoodCalories, searchFood } from '../lib/foodData.js';|g" calorie-love-tracker/src/components/PresetPicker.jsx

# Создаем недостающие файлы frontend если нужно
echo "📝 Проверка структуры frontend..."

# Создаем lib/utils.ts если его нет
if [ ! -f "calorie-love-tracker/src/lib/utils.ts" ]; then
    echo "📝 Создание lib/utils.ts..."
    mkdir -p calorie-love-tracker/src/lib
    cat > calorie-love-tracker/src/lib/utils.ts << 'EOF'
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
EOF
fi

# Создаем lib/foodData.js если его нет
if [ ! -f "calorie-love-tracker/src/lib/foodData.js" ]; then
    echo "📝 Создание lib/foodData.js..."
    cat > calorie-love-tracker/src/lib/foodData.js << 'EOF'
// Все локальные данные удалены. Только CalorieNinjas API:

const CALORIE_NINJAS_API_KEY = 'S+MDs4qFxUiE/WZHQXbHbw==TSlWYv6M8HzwQwKa';
const CALORIE_NINJAS_URL = 'https://api.calorieninjas.com/v1/nutrition?query=';

export const searchFood = async (query) => {
  const res = await fetch(CALORIE_NINJAS_URL + encodeURIComponent(query), {
    headers: { 'X-Api-Key': CALORIE_NINJAS_API_KEY }
  });
  const data = await res.json();
  return data.items || [];
};

export const getFoodCalories = async (foodName) => {
  const items = await searchFood(foodName);
  if (!items.length) return null;
  return items[0];
};
EOF
fi

# Создаем lib/presets.json если его нет
if [ ! -f "calorie-love-tracker/src/lib/presets.json" ]; then
    echo "📝 Создание lib/presets.json..."
    cat > calorie-love-tracker/src/lib/presets.json << 'EOF'
[
  {
    "title": "Офисный завтрак",
    "items": [
      { "name": "кофе растворимый", "grams": 200, "kcal": 4 },
      { "name": "сырники", "grams": 150, "kcal": 310 },
      { "name": "яблоко", "grams": 100, "kcal": 50 }
    ]
  },
  {
    "title": "Лёгкий ужин",
    "items": [
      { "name": "куриная грудка", "grams": 150, "kcal": 165 },
      { "name": "овощной салат", "grams": 100, "kcal": 60 }
    ]
  },
  {
    "title": "Рацион после тренировки",
    "items": [
      { "name": "банан", "grams": 100, "kcal": 89 },
      { "name": "творог", "grams": 200, "kcal": 160 },
      { "name": "протеиновый батончик", "grams": 60, "kcal": 220 }
    ]
  }
]
EOF
fi

# Полная очистка Docker кэша
echo "🧹 Полная очистка Docker..."
docker system prune -a -f
docker volume prune -f

# Удаляем все образы проекта
echo "🗑️ Удаление старых образов..."
docker rmi $(docker images "dieta*" -q) 2>/dev/null || true
docker rmi $(docker images "*dieta*" -q) 2>/dev/null || true

# Принудительная пересборка без кэша
echo "🔧 Принудительная пересборка всех контейнеров..."
docker-compose down --volumes --remove-orphans

# Сначала собираем и запускаем только API и Bot
echo "🚀 Запуск API и Bot контейнеров..."
docker-compose up -d api bot

# Ждем запуска API
echo "⏳ Ожидание запуска API..."
sleep 30

# Проверяем API
echo "🏥 Проверка API сервера..."
for i in {1..5}; do
    if curl -f http://localhost:8000/health; then
        echo "✅ API сервер запущен!"
        break
    else
        echo "⏳ Попытка $i/5 - API еще не готов..."
        sleep 10
    fi
done

# Теперь собираем frontend отдельно
echo "🔧 Сборка frontend..."
docker-compose build --no-cache frontend

# Запускаем frontend
echo "🚀 Запуск frontend..."
docker-compose up -d frontend

# Проверяем статус всех контейнеров
echo "📊 Финальный статус:"
docker-compose ps

# Проверяем логи
echo "📋 Последние логи API:"
docker-compose logs --tail=5 api

echo "📋 Последние логи Bot:"
docker-compose logs --tail=5 bot

echo "📋 Последние логи Frontend:"
docker-compose logs --tail=5 frontend

echo "✅ Исправление завершено!"
echo ""
echo "🌐 Доступные сервисы:"
echo "- API: http://5.129.198.80:8000"
echo "- Health: http://5.129.198.80:8000/health"
echo "- Docs: http://5.129.198.80:8000/docs"
echo "- Frontend: http://5.129.198.80:3000" 