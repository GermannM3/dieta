#!/usr/bin/env python3
"""
Простой тест SMTP для Rambler
"""

import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

def test_rambler_smtp():
    print("🔧 Тестирование Rambler SMTP...")
    print("=" * 40)
    
    # Настройки Rambler
    smtp_server = "smtp.rambler.ru"
    smtp_port = 465  # SSL
    username = "tvoy-calculator@rambler.ru"
    password = "Germ@nnM3"
    
    print(f"Сервер: {smtp_server}")
    print(f"Порт: {smtp_port}")
    print(f"Пользователь: {username}")
    print()
    
    try:
        print("🔌 Подключение к SMTP серверу...")
        
        # Подключение через SSL
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        print("✅ SSL соединение установлено")
        
        # Аутентификация
        print("🔐 Аутентификация...")
        server.login(username, password)
        print("✅ Аутентификация успешна")
        
        server.quit()
        print("✅ SMTP тест прошел успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка SMTP: {e}")
        print()
        print("🔄 Пробуем альтернативный порт 587...")
        
        try:
            # Попробуем STARTTLS
            server = smtplib.SMTP(smtp_server, 587)
            server.starttls()
            server.login(username, password)
            server.quit()
            print("✅ SMTP работает через порт 587!")
            print("📝 Обновите .env: SMTP_PORT=587")
            return True
        except Exception as e2:
            print(f"❌ Порт 587 тоже не работает: {e2}")
            return False

if __name__ == "__main__":
    print("🚀 Тест Rambler SMTP")
    print()
    success = test_rambler_smtp()
    print()
    if success:
        print("🎉 SMTP готов к работе!")
    else:
        print("💡 Возможные решения:")
        print("1. Проверьте пароль")
        print("2. Включите 'Внешние приложения' в настройках Rambler")
        print("3. Проверьте файрвол/антивирус") 