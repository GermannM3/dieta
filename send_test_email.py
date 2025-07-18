#!/usr/bin/env python3
"""
Тест отправки реального письма
"""

import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import random
import string

def generate_code():
    return ''.join(random.choices(string.digits, k=6))

def send_test_email():
    # Настройки Rambler
    smtp_server = "smtp.rambler.ru"
    smtp_port = 465
    username = "tvoy-calculator@rambler.ru"
    password = "Germ@nnM3"
    from_email = "tvoy-calculator@rambler.ru"
    
    # Запрашиваем email получателя
    to_email = input("Введите email для тестирования: ").strip()
    if not to_email:
        print("❌ Email не указан")
        return
    
    # Генерируем код
    code = generate_code()
    
    print(f"📧 Отправляем письмо на {to_email}")
    print(f"📋 Код подтверждения: {code}")
    
    try:
        # Создаем сообщение
        msg = MimeMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = "Тест SMTP - Твой Диетолог"
        
        # HTML письмо
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #4CAF50;">🎉 SMTP тест успешен!</h2>
                <p>Поздравляем! Система отправки email работает корректно.</p>
                
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                    <p style="margin: 0; font-size: 18px;">Тестовый код подтверждения:</p>
                    <h1 style="color: #4CAF50; font-size: 32px; margin: 10px 0; letter-spacing: 3px;">{code}</h1>
                </div>
                
                <p>✅ Rambler SMTP настроен правильно</p>
                <p>✅ Письма будут доставляться пользователям</p>
                <p>✅ Регистрация с подтверждением email работает</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    Это тестовое письмо от системы "Твой Диетолог"<br>
                    Отправлено: {smtp_server}:{smtp_port}
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MimeText(html_body, 'html', 'utf-8'))
        
        # Отправляем через SSL
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(username, password)
            server.send_message(msg)
        
        print("✅ Письмо отправлено успешно!")
        print("📬 Проверьте почту (включая папку спам)")
        print(f"📋 Код для проверки: {code}")
        
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")

if __name__ == "__main__":
    print("📧 Тест отправки email через Rambler")
    print("=" * 40)
    send_test_email() 