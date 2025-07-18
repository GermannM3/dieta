import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import os
from dotenv import load_dotenv
import logging
import random
import string
from typing import Optional

load_dotenv()

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # SMTP настройки из переменных окружения
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_username)
        
        # Проверяем настройки
        self.is_configured = bool(self.smtp_username and self.smtp_password)
        
        if not self.is_configured:
            logger.warning("SMTP не настроен. Письма не будут отправляться.")
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Отправка email"""
        if not self.is_configured:
            logger.warning(f"SMTP не настроен. Письмо не отправлено: {to_email}")
            return False
        
        try:
            # Создаем сообщение
            msg = MimeMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Добавляем текст
            msg.attach(MimeText(body, 'html' if is_html else 'plain', 'utf-8'))
            
            # Определяем тип подключения по порту
            if self.smtp_port == 465:
                # SSL соединение (например, Rambler, Gmail SSL)
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
            else:
                # STARTTLS соединение (стандартные порты 587, 25)
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.smtp_port != 25:  # Для порта 25 STARTTLS может не поддерживаться
                        server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
            
            logger.info(f"Email отправлен успешно: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки email {to_email}: {e}")
            return False
    
    def send_confirmation_email(self, to_email: str, confirmation_code: str) -> bool:
        """Отправка письма с подтверждением регистрации"""
        subject = "Подтверждение регистрации - Твой Диетолог"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #4CAF50;">🥗 Добро пожаловать в Твой Диетолог!</h2>
                <p>Спасибо за регистрацию в нашем сервисе персонального питания.</p>
                
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                    <p style="margin: 0; font-size: 18px;">Ваш код подтверждения:</p>
                    <h1 style="color: #4CAF50; font-size: 32px; margin: 10px 0; letter-spacing: 3px;">{confirmation_code}</h1>
                </div>
                
                <p>Введите этот код в приложении для завершения регистрации.</p>
                <p style="color: #666; font-size: 14px;">Код действителен в течение 24 часов.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    Если вы не регистрировались в нашем сервисе, проигнорируйте это письмо.<br>
                    С уважением, команда Твой Диетолог
                </p>
            </div>
        </body>
        </html>
        """
        return self.send_email(to_email, subject, body, is_html=True)
    
    def send_password_reset_email(self, to_email: str, reset_code: str) -> bool:
        """Отправка письма с восстановлением пароля"""
        subject = "Восстановление пароля - Твой Диетолог"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: #FF9800;">🔑 Восстановление пароля</h2>
                <p>Вы запросили восстановление пароля для аккаунта <strong>{to_email}</strong></p>
                
                <div style="background-color: #fff3e0; padding: 20px; border-radius: 5px; text-align: center; margin: 20px 0;">
                    <p style="margin: 0; font-size: 18px;">Ваш код восстановления:</p>
                    <h1 style="color: #FF9800; font-size: 32px; margin: 10px 0; letter-spacing: 3px;">{reset_code}</h1>
                </div>
                
                <p>Введите этот код в приложении для сброса пароля.</p>
                <p style="color: #d32f2f; font-weight: bold;">⚠️ Код действителен в течение 15 минут!</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                
                <p style="color: #999; font-size: 12px;">
                    Если вы не запрашивали восстановление пароля, проигнорируйте это письмо.<br>
                    С уважением, команда Твой Диетолог
                </p>
            </div>
        </body>
        </html>
        """
        return self.send_email(to_email, subject, body, is_html=True)
    
    @staticmethod
    def generate_confirmation_code() -> str:
        """Генерация 6-значного кода подтверждения"""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def get_smtp_config_examples() -> dict:
        """Примеры конфигураций SMTP для популярных провайдеров"""
        return {
            "Gmail": {
                "SMTP_SERVER": "smtp.gmail.com",
                "SMTP_PORT": "587",
                "SMTP_USERNAME": "your_email@gmail.com",
                "SMTP_PASSWORD": "your_app_password",  # Нужен App Password!
                "FROM_EMAIL": "your_email@gmail.com"
            },
            "Gmail_SSL": {
                "SMTP_SERVER": "smtp.gmail.com",
                "SMTP_PORT": "465",
                "SMTP_USERNAME": "your_email@gmail.com",
                "SMTP_PASSWORD": "your_app_password",
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
            },
            "Rambler_STARTTLS": {
                "SMTP_SERVER": "smtp.rambler.ru",
                "SMTP_PORT": "587",  # STARTTLS альтернатива
                "SMTP_USERNAME": "your_email@rambler.ru",
                "SMTP_PASSWORD": "your_password",
                "FROM_EMAIL": "your_email@rambler.ru"
            },
            "Outlook": {
                "SMTP_SERVER": "smtp-mail.outlook.com",
                "SMTP_PORT": "587",
                "SMTP_USERNAME": "your_email@outlook.com",
                "SMTP_PASSWORD": "your_password",
                "FROM_EMAIL": "your_email@outlook.com"
            }
        }

# Глобальный экземпляр сервиса
email_service = EmailService() 