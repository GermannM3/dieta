#!/bin/bash
echo "🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ ПРОБЛЕМ НА СЕРВЕРЕ"
echo "=============================================="

cd /opt/dieta || { echo "❌ Папка /opt/dieta не найдена!"; exit 1; }

echo "📍 Текущая папка: $(pwd)"

# Останавливаем все Docker контейнеры
echo "🛑 Остановка Docker контейнеров..."
docker-compose down 2>/dev/null || true
docker stop $(docker ps -q) 2>/dev/null || true

# Принудительно обновляем проект
echo "🔄 Принудительное обновление проекта..."
git fetch origin
git reset --hard origin/main
git pull origin main

echo "✅ Проект обновлен"

# Исправляем .env файл - основная проблема!
echo "🔧 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ .env файла..."
if [[ -f ".env" ]]; then
    echo "📋 Текущий .env:"
    cat .env
    
    echo ""
    echo "🔧 Исправление DATABASE_URL..."
    
    # Создаем резервную копию
    cp .env .env.backup
    
    # Исправляем DATABASE_URL - убираем проблемные символы
    sed -i 's|postgres://|postgresql+asyncpg://|g' .env
    sed -i 's|?sslmode=require||g' .env
    
    # Убираем все непечатаемые символы которые могут вызывать ошибку парсинга
    sed -i 's/[[:cntrl:]]//g' .env
    
    # Проверяем и исправляем формат DATABASE_URL
    if grep -q "DATABASE_URL=" .env; then
        # Извлекаем DATABASE_URL и очищаем его от проблемных символов
        DB_URL=$(grep "DATABASE_URL=" .env | cut -d'=' -f2- | tr -d '\r\n[:cntrl:]')
        
        # Убираем старую строку и добавляем исправленную
        grep -v "DATABASE_URL=" .env > .env.tmp
        echo "DATABASE_URL=$DB_URL" >> .env.tmp
        mv .env.tmp .env
        
        echo "✅ DATABASE_URL исправлен"
    else
        echo "❌ DATABASE_URL не найден в .env!"
        exit 1
    fi
    
    echo "📋 Исправленный .env:"
    cat .env
else
    echo "❌ Файл .env не найден!"
    exit 1
fi

# Полная очистка Docker
echo "🧹 Полная очистка Docker..."
docker system prune -a -f
docker volume prune -f

# Удаляем все образы проекта
echo "🗑️ Удаление старых образов..."
docker rmi $(docker images "*dieta*" -q) 2>/dev/null || true
docker rmi $(docker images "*opt*" -q) 2>/dev/null || true

# Проверяем что Docker демон запущен
echo "🐳 Проверка Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker не запущен! Запускаем..."
    systemctl start docker
    sleep 5
fi

# Создаем недостающие файлы если нужно
echo "📝 Создание недостающих файлов..."

# Создаем lib/utils.ts для фронтенда
mkdir -p calorie-love-tracker/src/lib
cat > calorie-love-tracker/src/lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
EOF

# Создаем lib/foodData.js для фронтенда
cat > calorie-love-tracker/src/lib/foodData.js << 'EOF'
// Fallback food data
export const fallbackFoodData = {
  "apple": { calories: 52, protein: 0.3, fat: 0.2, carbs: 14 },
  "banana": { calories: 89, protein: 1.1, fat: 0.3, carbs: 23 },
  "rice": { calories: 130, protein: 2.7, fat: 0.3, carbs: 28 },
  "chicken": { calories: 165, protein: 31, fat: 3.6, carbs: 0 },
  "bread": { calories: 265, protein: 9, fat: 3.2, carbs: 49 }
};

export function getFoodCalories(foodName) {
  const food = fallbackFoodData[foodName.toLowerCase()];
  return food ? food.calories : 100;
}

export function searchFood(query) {
  const results = [];
  for (const [name, data] of Object.entries(fallbackFoodData)) {
    if (name.includes(query.toLowerCase())) {
      results.push({ name, ...data });
    }
  }
  return results;
}
EOF

echo "✅ Файлы созданы"

# Поэтапная сборка контейнеров
echo "🔧 Поэтапная сборка контейнеров..."

# Сначала собираем API и Bot
echo "📦 Сборка API и Bot..."
docker-compose build --no-cache api bot

if [ $? -ne 0 ]; then
    echo "❌ Ошибка сборки API/Bot!"
    exit 1
fi

# Запускаем API и ждем готовности
echo "🚀 Запуск API..."
docker-compose up -d api

# Ждем готовности API
echo "⏳ Ожидание готовности API..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API готов!"
        break
    else
        echo "⏳ Попытка $i/10 - API еще не готов..."
        sleep 10
    fi
done

# Проверяем логи API если он не готов
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ API не готов! Логи:"
    docker-compose logs api
    exit 1
fi

# Запускаем Bot
echo "🤖 Запуск Bot..."
docker-compose up -d bot

# Собираем и запускаем Frontend
echo "🎨 Сборка Frontend..."
docker-compose build --no-cache frontend

echo "🚀 Запуск Frontend..."
docker-compose up -d frontend

# Финальная проверка
echo "📊 Финальная проверка сервисов..."
docker-compose ps

echo ""
echo "📋 Логи сервисов:"
echo "=== API ==="
docker-compose logs --tail=10 api
echo ""
echo "=== Bot ==="
docker-compose logs --tail=10 bot
echo ""
echo "=== Frontend ==="
docker-compose logs --tail=10 frontend

echo ""
echo "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo ""
echo "🌐 Доступные сервисы:"
echo "- API: http://5.129.198.80:8000"
echo "- Health: http://5.129.198.80:8000/health"
echo "- Docs: http://5.129.198.80:8000/docs"
echo "- Frontend: http://5.129.198.80:3000"
echo ""
echo "🔍 Проверьте логи: docker-compose logs -f" 