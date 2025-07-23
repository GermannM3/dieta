#!/usr/bin/env python3
"""
Скрипт для тестирования премиум функций
"""

import asyncio
import sys
import os

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.payment_system.payment_operations import check_premium, PaymentManager
from database.init_database import async_session_maker
from database.crud import get_user_by_tg_id

async def test_premium_functions():
    """Тестирование премиум функций"""
    print("🔍 Тестирование премиум функций...")
    
    # Тестовый пользователь (админ)
    test_user_id = 389694638
    
    print(f"\n1️⃣ Проверка премиум статуса для пользователя {test_user_id}:")
    premium_status = check_premium(test_user_id)
    print(f"   Премиум статус: {'✅ АКТИВЕН' if premium_status else '❌ НЕ АКТИВЕН'}")
    
    print(f"\n2️⃣ Проверка подписки 'diet_consultant':")
    diet_subscription = await PaymentManager.check_subscription(test_user_id, 'diet_consultant')
    print(f"   Подписка диетолог: {'✅ АКТИВНА' if diet_subscription else '❌ НЕ АКТИВНА'}")
    
    print(f"\n3️⃣ Проверка подписки 'menu_generator':")
    menu_subscription = await PaymentManager.check_subscription(test_user_id, 'menu_generator')
    print(f"   Подписка меню: {'✅ АКТИВНА' if menu_subscription else '❌ НЕ АКТИВНА'}")
    
    print(f"\n4️⃣ Информация о подписках:")
    diet_info = await PaymentManager.get_subscription_info(test_user_id, 'diet_consultant')
    menu_info = await PaymentManager.get_subscription_info(test_user_id, 'menu_generator')
    
    if diet_info:
        print(f"   Диетолог: {diet_info}")
    else:
        print(f"   Диетолог: нет активной подписки")
    
    if menu_info:
        print(f"   Меню: {menu_info}")
    else:
        print(f"   Меню: нет активной подписки")
    
    print(f"\n5️⃣ Проверка пользователя в БД:")
    async with async_session_maker() as session:
        user = await get_user_by_tg_id(session, test_user_id)
        if user:
            print(f"   Пользователь найден: {user.name}")
            print(f"   is_premium: {getattr(user, 'is_premium', 'поле не найдено')}")
        else:
            print(f"   Пользователь не найден в БД")

if __name__ == "__main__":
    asyncio.run(test_premium_functions()) 