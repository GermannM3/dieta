#!/bin/bash

echo "🔍 Тестирование API эндпоинтов..."

# Базовый URL для тестов
BASE_URL="http://5.129.198.80"

echo "1️⃣ Проверка API документации..."
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" "$BASE_URL/api/docs"

echo "2️⃣ Тест поиска продуктов..."
curl -s -X POST "$BASE_URL/api/search_food" \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  -o /dev/null -w "HTTP Status: %{http_code}\n"

echo "3️⃣ Тест расчета калорий..."
curl -s -X POST "$BASE_URL/api/calculate_calories" \
  -H "Content-Type: application/json" \
  -d '{"food_name": "яблоко", "quantity": 100}' \
  -o /dev/null -w "HTTP Status: %{http_code}\n"

echo "4️⃣ Тест регистрации..."
curl -s -X POST "$BASE_URL/api/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}' \
  -o /dev/null -w "HTTP Status: %{http_code}\n"

echo "5️⃣ Тест входа..."
curl -s -X POST "$BASE_URL/api/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "germannm@vk.com", "password": "Germ@nnM3"}' \
  -o /dev/null -w "HTTP Status: %{http_code}\n"

echo "✅ Тестирование завершено!" 