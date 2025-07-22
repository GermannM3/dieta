#!/bin/bash

echo "🔧 НАСТРОЙКА ПЛАТЕЖНОЙ СИСТЕМЫ..."

echo "1️⃣ Остановка бота..."
pkill -f "python main.py" || true

echo "2️⃣ Добавление таблицы подписок..."
python add_subscription_table.py

echo "3️⃣ Тестирование платежной системы..."
python test_payments.py

echo "4️⃣ Запуск бота..."
python main.py &

echo "✅ Платежная система настроена!"
echo ""
echo "📋 Доступные команды:"
echo "• /diet_consultant - Купить подписку на личного диетолога"
echo "• /menu_generator - Купить подписку на генерацию меню"
echo "• /subscription - Проверить текущие подписки"
echo ""
echo "💳 Тестовые данные для YooMoney:"
echo "• Номер карты: 5555 5555 5555 4444"
echo "• CVC: любой 3-значный код"
echo "• Дата: любая будущая дата"
echo ""
echo "🎯 Теперь функции 'Личный диетолог' и 'Сгенерировать меню' требуют подписку!" 