#!/bin/bash

echo "🔍 Тестирование API эндпоинтов..."

echo "1️⃣ Проверка API документации..."
curl -I https://tvoi-kalkulyator.ru/docs

echo "2️⃣ Тест поиска продуктов..."
curl -X POST "https://tvoi-kalkulyator.ru/api/search_food" \
  -H "Content-Type: application/json" \
  -d '{"query": "яблоко"}' \
  -w "\nHTTP Status: %{http_code}\n"

echo "3️⃣ Тест расчета калорий..."
curl -X POST "https://tvoi-kalkulyator.ru/api/calculate_calories" \
  -H "Content-Type: application/json" \
  -d '{"foods": [{"name": "яблоко", "amount": 100}]}' \
  -w "\nHTTP Status: %{http_code}\n"

echo "4️⃣ Тест регистрации..."
curl -X POST "https://tvoi-kalkulyator.ru/api/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}' \
  -w "\nHTTP Status: %{http_code}\n"

echo "5️⃣ Тест входа..."
curl -X POST "https://tvoi-kalkulyator.ru/api/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "germannm@vk.com", "password": "Germ@nnM3"}' \
  -w "\nHTTP Status: %{http_code}\n"

echo "✅ Тестирование завершено!" 