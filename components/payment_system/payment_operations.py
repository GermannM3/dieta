import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
from yookassa import Configuration, Payment
from yookassa.domain.exceptions import YooKassaError
from database.init_database import async_session_maker, Subscription
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

# Настройки YooMoney
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID', '381764678')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY', 'TEST:132209')
YOOKASSA_PAYMENT_TOKEN = os.getenv('YOOKASSA_PAYMENT_TOKEN', '381764678:TEST:132209')

# Настройки подписки
SUBSCRIPTION_PRICE = int(os.getenv('SUBSCRIPTION_PRICE', '200'))
SUBSCRIPTION_DURATION_DAYS = int(os.getenv('SUBSCRIPTION_DURATION_DAYS', '7'))

# Инициализация YooMoney
Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

class PaymentManager:
    """Менеджер для работы с платежами YooMoney"""
    
    @staticmethod
    async def create_payment(user_id: int, subscription_type: str) -> dict:
        """
        Создает платеж для подписки
        
        Args:
            user_id: ID пользователя в Telegram
            subscription_type: Тип подписки ('diet_consultant' или 'menu_generator')
        
        Returns:
            dict: Информация о платеже
        """
        try:
            # Создаем уникальный ID платежа
            payment_idempotence_key = str(uuid.uuid4())
            
            # Определяем описание в зависимости от типа подписки
            if subscription_type == 'diet_consultant':
                title = "Личный диетолог"
                description = "Персональные консультации диетолога на 7 дней"
            elif subscription_type == 'menu_generator':
                title = "Генерация меню"
                description = "Персональное меню на 7 дней"
            else:
                raise ValueError(f"Неизвестный тип подписки: {subscription_type}")
            
            # Создаем платеж в YooMoney
            payment = Payment.create(
                {
                    "amount": {
                        "value": str(SUBSCRIPTION_PRICE),
                        "currency": "RUB"
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": "https://t.me/tvoy_diet_bot"
                    },
                    "capture": True,
                    "description": f"{title} - {description}",
                    "metadata": {
                        "user_id": str(user_id),
                        "subscription_type": subscription_type
                    }
                },
                payment_idempotence_key
            )
            
            # Сохраняем информацию о подписке в БД
            async with async_session_maker() as session:
                subscription = Subscription(
                    user_id=user_id,
                    subscription_type=subscription_type,
                    payment_id=payment.id,
                    amount=SUBSCRIPTION_PRICE,
                    currency='RUB',
                    status='pending',
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=SUBSCRIPTION_DURATION_DAYS)
                )
                session.add(subscription)
                await session.commit()
            
            return {
                'payment_id': payment.id,
                'confirmation_url': payment.confirmation.confirmation_url,
                'amount': SUBSCRIPTION_PRICE,
                'currency': 'RUB',
                'title': title,
                'description': description
            }
            
        except YooKassaError as e:
            print(f"Ошибка YooMoney: {e}")
            raise
        except Exception as e:
            print(f"Ошибка создания платежа: {e}")
            raise
    
    @staticmethod
    async def confirm_payment(payment_id: str) -> bool:
        """
        Подтверждает успешный платеж
        
        Args:
            payment_id: ID платежа в YooMoney
        
        Returns:
            bool: True если платеж подтвержден успешно
        """
        try:
            # Получаем информацию о платеже из YooMoney
            payment = Payment.find_one(payment_id)
            
            if payment.status == 'succeeded':
                # Обновляем статус подписки в БД
                async with async_session_maker() as session:
                    subscription = await session.execute(
                        select(Subscription).where(Subscription.payment_id == payment_id)
                    )
                    subscription = subscription.scalar_one_or_none()
                    
                    if subscription:
                        subscription.status = 'completed'
                        await session.commit()
                        return True
                    else:
                        print(f"Подписка с payment_id {payment_id} не найдена")
                        return False
            else:
                print(f"Платеж {payment_id} не был успешным. Статус: {payment.status}")
                return False
                
        except YooKassaError as e:
            print(f"Ошибка YooMoney при подтверждении платежа: {e}")
            return False
        except Exception as e:
            print(f"Ошибка подтверждения платежа: {e}")
            return False
    
    @staticmethod
    async def check_subscription(user_id: int, subscription_type: str) -> bool:
        """
        Проверяет активную подписку пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            subscription_type: Тип подписки ('diet_consultant' или 'menu_generator')
        
        Returns:
            bool: True если подписка активна
        """
        try:
            async with async_session_maker() as session:
                # Ищем активную подписку
                subscription = await session.execute(
                    select(Subscription).where(
                        and_(
                            Subscription.user_id == user_id,
                            Subscription.subscription_type == subscription_type,
                            Subscription.status == 'completed',
                            Subscription.end_date > datetime.utcnow()
                        )
                    )
                )
                subscription = subscription.scalar_one_or_none()
                
                return subscription is not None
                
        except Exception as e:
            print(f"Ошибка проверки подписки: {e}")
            return False
    
    @staticmethod
    async def get_subscription_info(user_id: int, subscription_type: str) -> Optional[dict]:
        """
        Получает информацию о подписке пользователя
        
        Args:
            user_id: ID пользователя в Telegram
            subscription_type: Тип подписки ('diet_consultant' или 'menu_generator')
        
        Returns:
            dict: Информация о подписке или None
        """
        try:
            async with async_session_maker() as session:
                subscription = await session.execute(
                    select(Subscription).where(
                        and_(
                            Subscription.user_id == user_id,
                            Subscription.subscription_type == subscription_type,
                            Subscription.status == 'completed'
                        )
                    ).order_by(Subscription.end_date.desc())
                )
                subscription = subscription.scalar_one_or_none()
                
                if subscription:
                    return {
                        'id': subscription.id,
                        'type': subscription.subscription_type,
                        'status': subscription.status,
                        'start_date': subscription.start_date,
                        'end_date': subscription.end_date,
                        'is_active': subscription.end_date > datetime.utcnow(),
                        'days_left': (subscription.end_date - datetime.utcnow()).days if subscription.end_date > datetime.utcnow() else 0
                    }
                return None
                
        except Exception as e:
            print(f"Ошибка получения информации о подписке: {e}")
            return None


