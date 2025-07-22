#!/usr/bin/env python3
"""
Скрипт для тестирования платежной системы
"""

import asyncio
import os
from components.payment_system.payment_operations import PaymentManager

async def test_payment_system():
    """Тестирует платежную систему"""
    print("🧪 Тестирование платежной системы...")
    
    # Тестовый пользователь
    test_user_id = 389694638  # ID админа
    
    try:
        # Тест 1: Проверка подписки (должна быть неактивна)
        print("\n1️⃣ Проверка подписки на диетолога...")
        has_subscription = await PaymentManager.check_subscription(test_user_id, 'diet_consultant')
        print(f"Результат: {has_subscription}")
        
        # Тест 2: Создание платежа
        print("\n2️⃣ Создание платежа для диетолога...")
        payment_info = await PaymentManager.create_payment(test_user_id, 'diet_consultant')
        print(f"Платеж создан: {payment_info['payment_id']}")
        print(f"Сумма: {payment_info['amount']} {payment_info['currency']}")
        print(f"Название: {payment_info['title']}")
        
        # Тест 3: Проверка информации о подписке
        print("\n3️⃣ Получение информации о подписке...")
        subscription_info = await PaymentManager.get_subscription_info(test_user_id, 'diet_consultant')
        if subscription_info:
            print(f"Статус: {subscription_info['status']}")
            print(f"Активна: {subscription_info['is_active']}")
            print(f"Дней осталось: {subscription_info['days_left']}")
        else:
            print("Подписка не найдена")
        
        # Тест 4: Создание платежа для меню
        print("\n4️⃣ Создание платежа для меню...")
        menu_payment = await PaymentManager.create_payment(test_user_id, 'menu_generator')
        print(f"Платеж создан: {menu_payment['payment_id']}")
        
        print("\n✅ Все тесты выполнены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        raise

async def main():
    """Главная функция"""
    print("🧪 Запуск тестов платежной системы...")
    await test_payment_system()
    print("✅ Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(main()) 