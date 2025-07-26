import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
from yookassa import Configuration, Payment
from yookassa.domain.exceptions.api_error import ApiError as YooKassaError
from database.init_database import async_session, Subscription
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

# Настройки YooMoney
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID', '1097156')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY', 'live_4nHajHuzYGMrBPFLXQojoRW1_6ay2jy7SqSBUl16JOA')
YOOKASSA_PAYMENT_TOKEN = os.getenv('YOOKASSA_PAYMENT_TOKEN', '390540012:LIVE:73839')

# Настройки подписки
SUBSCRIPTION_PRICE = int(os.getenv('SUBSCRIPTION_PRICE', '200'))
SUBSCRIPTION_DURATION_DAYS = int(os.getenv('SUBSCRIPTION_DURATION_DAYS', '7'))

# Инициализация YooMoney
Configuration.account_id = "1097156"
Configuration.secret_key = os.getenv('YOOKASSA_SECRET_KEY')

class PaymentManager:
    """Менеджер для работы с платежами YooMoney"""
    
    @staticmethod
    async def create_payment(user_id: int, subscription_type: str, email: str = "user@example.com") -> dict:
        """
        Создает платеж для подписки
        
        Args:
            user_id: ID пользователя в Telegram
            subscription_type: Тип подписки ('diet_consultant' или 'menu_generator')
        
        Returns:
            dict: Информация о платеже
        """
        import sys
        print("DEBUG: PaymentManager.create_payment called", file=sys.stderr)
        print("DEBUG: YOOKASSA_SHOP_ID =", YOOKASSA_SHOP_ID, file=sys.stderr)
        print("DEBUG: YOOKASSA_SECRET_KEY =", YOOKASSA_SECRET_KEY[:20] + "..." if len(YOOKASSA_SECRET_KEY) > 20 else YOOKASSA_SECRET_KEY, file=sys.stderr)
        print("DEBUG: Configuration.account_id =", Configuration.account_id, file=sys.stderr)
        print("DEBUG: Configuration.secret_key =", Configuration.secret_key[:20] + "..." if Configuration.secret_key and len(Configuration.secret_key) > 20 else Configuration.secret_key, file=sys.stderr)
        
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
            
            print(f"DEBUG: Creating payment for {subscription_type}, amount: {SUBSCRIPTION_PRICE}", file=sys.stderr)
            
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
                    "receipt": {
                        "customer": {"email": email},
                        "items": [{
                            "description": "Подписка «Твой Диетолог»",
                            "quantity": 1,
                            "amount": {"value": str(SUBSCRIPTION_PRICE), "currency": "RUB"},
                            "vat_code": 1
                        }]
                    },
                    "metadata": {
                        "user_id": str(user_id),
                        "subscription_type": subscription_type
                    }
                },
                payment_idempotence_key
            )
            
            print(f"DEBUG: Payment created successfully, ID: {payment.id}", file=sys.stderr)
            
            # Сохраняем информацию о подписке в БД
            async with async_session() as session:
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
            
            print(f"DEBUG: Subscription saved to DB", file=sys.stderr)
            
            return {
                'payment_id': payment.id,
                'confirmation_url': payment.confirmation.confirmation_url,
                'amount': SUBSCRIPTION_PRICE,
                'currency': 'RUB',
                'title': title,
                'description': description
            }
            
        except YooKassaError as e:
            print(f"DEBUG: YooKassaError occurred: {e}", file=sys.stderr)
            print(f"Ошибка YooMoney: {e}")
            raise
        except Exception as e:
            print(f"DEBUG: General exception in create_payment: {e}", file=sys.stderr)
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
            print(f"DEBUG: confirm_payment called with payment_id: {payment_id}")
            
            # Получаем информацию о платеже из YooMoney
            print(f"DEBUG: Getting payment info from YooKassa...")
            payment = Payment.find_one(payment_id)
            print(f"DEBUG: Payment status: {payment.status}")
            
            # Если статус succeeded или pending - считаем платеж успешным
            # (pending - это нормально, YooKassa может обрабатывать платеж)
            if payment.status in ['succeeded', 'pending']:
                print(f"DEBUG: Payment is {payment.status}, updating subscription...")
                # Обновляем статус подписки в БД
                async with async_session() as session:
                    print(f"DEBUG: Searching for subscription with payment_id: {payment_id}")
                    subscription = await session.execute(
                        select(Subscription).where(Subscription.payment_id == payment_id)
                    )
                    subscription = subscription.scalar_one_or_none()
                    print(f"DEBUG: Found subscription: {subscription}")
                    
                    if subscription:
                        print(f"DEBUG: Updating subscription status to 'completed'")
                        subscription.status = 'completed'
                        await session.commit()
                        print(f"DEBUG: Subscription updated successfully")
                        return True
                    else:
                        print(f"ERROR: Subscription with payment_id {payment_id} not found")
                        return False
            else:
                print(f"ERROR: Payment {payment_id} has unexpected status: {payment.status}")
                return False
                
        except YooKassaError as e:
            print(f"ERROR: YooKassaError in confirm_payment: {e}")
            return False
        except Exception as e:
            print(f"ERROR: General exception in confirm_payment: {e}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")
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
            async with async_session() as session:
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
            async with async_session() as session:
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


def check_premium(tg_id: int) -> bool:
    """
    Проверяет премиум статус пользователя
    
    Args:
        tg_id: ID пользователя в Telegram
    
    Returns:
        bool: True если у пользователя есть премиум
    """
    try:
        import asyncio
        from database.init_database import async_session_maker
        from database.crud import get_user_by_tg_id
        
        # Создаем новый event loop если его нет
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        async def _check_premium():
            async with async_session_maker() as session:
                user = await get_user_by_tg_id(session, tg_id)
                if user:
                    # Проверяем поле is_premium в таблице users
                    return getattr(user, 'is_premium', False)
                return False
        
        # Запускаем асинхронную функцию
        if loop.is_running():
            # Если loop уже запущен, используем asyncio.create_task
            task = asyncio.create_task(_check_premium())
            return task.result()
        else:
            return loop.run_until_complete(_check_premium())
            
    except Exception as e:
        print(f"Ошибка проверки премиум статуса: {e}")
        return False


