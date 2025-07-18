#!/usr/bin/env python3
"""
Скрипт для тестирования SMTP настроек
Запуск: python test_smtp.py
"""

import asyncio
from api.email_service import email_service
from dotenv import load_dotenv
import os

load_dotenv()

async def test_smtp():
    print("🔧 Тестирование SMTP настроек...")
    print("=" * 50)
    
    # Проверяем настройки
    print(f"SMTP Сервер: {email_service.smtp_server}")
    print(f"SMTP Порт: {email_service.smtp_port}")
    print(f"SMTP Пользователь: {email_service.smtp_username}")
    print(f"Отправитель: {email_service.from_email}")
    print(f"SMTP настроен: {'✅ Да' if email_service.is_configured else '❌ Нет'}")
    print()
    
    if not email_service.is_configured:
        print("❌ SMTP не настроен!")
        print("Проверьте переменные в .env файле:")
        print("- SMTP_SERVER")
        print("- SMTP_PORT") 
        print("- SMTP_USERNAME")
        print("- SMTP_PASSWORD")
        print("- FROM_EMAIL")
        return
    
    # Запрашиваем email для теста
    test_email = input("Введите email для тестирования (или нажмите Enter для пропуска): ").strip()
    
    if not test_email:
        print("📝 Тест пропущен. Для тестирования нужен email.")
        return
    
    print(f"📧 Отправляем тестовое письмо на {test_email}...")
    
    # Генерируем тестовый код
    test_code = email_service.generate_confirmation_code()
    
    # Отправляем письмо
    success = email_service.send_confirmation_email(test_email, test_code)
    
    if success:
        print("✅ Письмо отправлено успешно!")
        print(f"📋 Код подтверждения: {test_code}")
        print("📬 Проверьте почту (в том числе папку спам)")
    else:
        print("❌ Ошибка отправки письма!")
        print("Возможные причины:")
        print("1. Неверные настройки SMTP")
        print("2. Блокировка антивирусом/файрволом")
        print("3. Ограничения почтового провайдера")
        print("4. Неверный пароль")
        print()
        print("Для Rambler попробуйте альтернативные настройки:")
        print("SMTP_PORT=587 (вместо 465)")

def main():
    print("🚀 SMTP Тестер - Твой Диетолог")
    print()
    
    try:
        asyncio.run(test_smtp())
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    
    print("\n🏁 Завершено")

if __name__ == "__main__":
    main() 