#!/bin/bash

echo "🔍 Проверка DNS и SSL..."

echo "📡 Проверяем DNS записи:"
echo "tvoi-kalkulyator.ru:"
nslookup tvoi-kalkulyator.ru
echo ""

echo "твой-калькулятор.рф:"
nslookup твой-калькулятор.рф
echo ""

echo "🌐 Проверяем HTTP:"
curl -I http://tvoi-kalkulyator.ru
echo ""

echo "🔒 Проверяем HTTPS:"
curl -I https://tvoi-kalkulyator.ru
echo ""

echo "✅ Проверка завершена!" 