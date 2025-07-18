#!/usr/bin/env python3
"""
Скрипт для настройки SMTP на сервере
"""

import os
import sys

def setup_smtp():
    """Настройка SMTP для отправки email"""
    print("🔧 Настройка SMTP для отправки email")
    print("=" * 50)
    
    # Проверяем существующие настройки
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ Файл {env_file} найден")
        
        # Читаем существующие настройки
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем, есть ли уже SMTP настройки
        if 'SMTP_SERVER' in content:
            print("⚠️ SMTP настройки уже существуют в .env файле")
            print("Текущие настройки:")
            for line in content.split('\n'):
                if line.startswith('SMTP_') or line.startswith('FROM_EMAIL'):
                    print(f"  {line}")
            return
        
        # Добавляем SMTP настройки
        smtp_config = """
# SMTP Configuration для отправки email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com
"""
        
        with open(env_file, 'a', encoding='utf-8') as f:
            f.write(smtp_config)
        
        print("✅ SMTP настройки добавлены в .env файл")
        print("📝 Не забудьте заменить значения на реальные:")
        print("  - SMTP_USERNAME: ваш email")
        print("  - SMTP_PASSWORD: пароль приложения (не обычный пароль!)")
        print("  - FROM_EMAIL: email для отправки")
        
    else:
        print(f"❌ Файл {env_file} не найден")
        print("Создайте файл .env с настройками")

def test_smtp():
    """Тест SMTP подключения"""
    print("\n🧪 Тестирование SMTP подключения")
    print("=" * 50)
    
    try:
        from api.email_service import EmailService
        
        email_service = EmailService()
        
        if email_service.is_configured:
            print("✅ SMTP настроен")
            print(f"  Сервер: {email_service.smtp_server}")
            print(f"  Порт: {email_service.smtp_port}")
            print(f"  Пользователь: {email_service.smtp_username}")
            print(f"  От: {email_service.from_email}")
            
            # Тестируем отправку
            test_email = "test@example.com"
            result = email_service.send_email(
                to_email=test_email,
                subject="Тест SMTP",
                body="Это тестовое письмо для проверки SMTP настроек."
            )
            
            if result:
                print("✅ Тестовое письмо отправлено успешно")
            else:
                print("❌ Ошибка отправки тестового письма")
        else:
            print("❌ SMTP не настроен")
            print("Добавьте настройки SMTP в .env файл")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования SMTP: {e}")

def show_examples():
    """Показать примеры настроек для разных провайдеров"""
    print("\n📋 Примеры настроек SMTP")
    print("=" * 50)
    
    examples = {
        "Gmail": {
            "SMTP_SERVER": "smtp.gmail.com",
            "SMTP_PORT": "587",
            "SMTP_USERNAME": "your_email@gmail.com",
            "SMTP_PASSWORD": "your_app_password",  # Нужен App Password!
            "FROM_EMAIL": "your_email@gmail.com"
        },
        "Yandex": {
            "SMTP_SERVER": "smtp.yandex.ru",
            "SMTP_PORT": "587",
            "SMTP_USERNAME": "your_email@yandex.ru",
            "SMTP_PASSWORD": "your_password",
            "FROM_EMAIL": "your_email@yandex.ru"
        },
        "Mail.ru": {
            "SMTP_SERVER": "smtp.mail.ru",
            "SMTP_PORT": "587",
            "SMTP_USERNAME": "your_email@mail.ru",
            "SMTP_PASSWORD": "your_password",
            "FROM_EMAIL": "your_email@mail.ru"
        },
        "Rambler": {
            "SMTP_SERVER": "smtp.rambler.ru",
            "SMTP_PORT": "465",  # SSL
            "SMTP_USERNAME": "your_email@rambler.ru",
            "SMTP_PASSWORD": "your_password",
            "FROM_EMAIL": "your_email@rambler.ru"
        }
    }
    
    for provider, config in examples.items():
        print(f"\n{provider}:")
        for key, value in config.items():
            print(f"  {key}={value}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            setup_smtp()
        elif command == "test":
            test_smtp()
        elif command == "examples":
            show_examples()
        else:
            print("Использование:")
            print("  python setup_smtp.py setup    - настроить SMTP")
            print("  python setup_smtp.py test     - протестировать SMTP")
            print("  python setup_smtp.py examples - показать примеры")
    else:
        print("🔧 Настройка SMTP для отправки email")
        print("=" * 50)
        setup_smtp()
        test_smtp()
        show_examples() 