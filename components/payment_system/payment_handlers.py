from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.init_database import async_session, User, Subscription
from sqlalchemy import select
from .payment_operations import PaymentManager
import os
import json

router = Router()

# Состояния для FSM
class PaymentStates(StatesGroup):
    waiting_for_payment = State()

# Настройки платежей
YOOKASSA_PAYMENT_TOKEN = os.getenv('YOOKASSA_PAYMENT_TOKEN', '390540012:LIVE:73839')
SUBSCRIPTION_PRICE = int(os.getenv('SUBSCRIPTION_PRICE', '200'))

@router.message(Command("diet_consultant"))
async def diet_consultant_handler(message: Message, state: FSMContext):
    """Обработчик команды личного диетолога"""
    user_id = message.from_user.id
    
    # Проверяем активную подписку
    has_subscription = await PaymentManager.check_subscription(user_id, 'diet_consultant')
    
    if has_subscription:
        await message.answer(
            "🎯 У вас есть активная подписка на личного диетолога!\n\n"
            "Вы можете задавать любые вопросы о питании и получать персональные рекомендации.\n\n"
            "Просто напишите ваш вопрос, и я отвечу как ваш личный диетолог!"
        )
        await state.clear()
    else:
        # Показываем информацию о подписке
        await message.answer(
            "👨‍⚕️ <b>Личный диетолог</b>\n\n"
            "Получите персональные консультации от ИИ-диетолога:\n"
            "• Ответы на любые вопросы о питании\n"
            "• Персональные рекомендации по диете\n"
            "• Анализ вашего рациона\n"
            "• Советы по достижению целей\n\n"
            "💰 <b>Стоимость:</b> 200₽ за 7 дней\n\n"
            "Для покупки подписки нажмите кнопку ниже:",
            parse_mode="HTML"
        )
        
        # Создаем платеж
        try:
            payment_info = await PaymentManager.create_payment(user_id, 'diet_consultant')
            
            # Отправляем счет
            await message.bot.send_invoice(
                chat_id=message.chat.id,
                title="Личный диетолог",
                description="Персональные консультации диетолога на 7 дней",
                payload=payment_info['payment_id'],
                currency="RUB",
                prices=[LabeledPrice(label="Подписка на 7 дней", amount=SUBSCRIPTION_PRICE * 100)],
                provider_token=YOOKASSA_PAYMENT_TOKEN,
                need_email=True,
                send_email_to_provider=True,
                provider_data=json.dumps({
                    "receipt": {
                        "items": [
                            {
                                "description": "Подписка на личного диетолога на 7 дней",
                                "quantity": 1,
                                "amount": {
                                    "value": float(SUBSCRIPTION_PRICE),
                                    "currency": "RUB"
                                },
                                "vat_code": 1,
                                "payment_mode": "full_payment",
                                "payment_subject": "service"
                            }
                        ],
                        "tax_system_code": 1
                    }
                })
            )
            
            await state.set_state(PaymentStates.waiting_for_payment)
            
        except Exception as e:
            await message.answer(
                "❌ Произошла ошибка при создании платежа. Попробуйте позже."
            )
            print(f"Ошибка создания платежа для диетолога: {e}")

@router.message(Command("menu_generator"))
async def menu_generator_handler(message: Message, state: FSMContext):
    """Обработчик команды генерации меню"""
    user_id = message.from_user.id
    
    # Проверяем активную подписку
    has_subscription = await PaymentManager.check_subscription(user_id, 'menu_generator')
    
    if has_subscription:
        await message.answer(
            "🍽️ У вас есть активная подписка на генерацию меню!\n\n"
            "Я могу создать для вас персональное меню на любой период.\n\n"
            "Просто напишите, на сколько дней вам нужно меню, и я его создам!"
        )
        await state.clear()
    else:
        # Показываем информацию о подписке
        await message.answer(
            "🍽️ <b>Генерация персонального меню</b>\n\n"
            "Получите персональное меню, созданное специально для вас:\n"
            "• Учет ваших целей и предпочтений\n"
            "• Сбалансированное питание\n"
            "• Разнообразные блюда\n"
            "• Подробные рецепты\n\n"
            "💰 <b>Стоимость:</b> 200₽ за 7 дней\n\n"
            "Для покупки подписки нажмите кнопку ниже:",
            parse_mode="HTML"
        )
        
        # Создаем платеж
        try:
            payment_info = await PaymentManager.create_payment(user_id, 'menu_generator')
            
            # Отправляем счет
            await message.bot.send_invoice(
                chat_id=message.chat.id,
                title="Генерация меню",
                description="Персональное меню на 7 дней",
                payload=payment_info['payment_id'],
                currency="RUB",
                prices=[LabeledPrice(label="Подписка на 7 дней", amount=SUBSCRIPTION_PRICE * 100)],
                provider_token=YOOKASSA_PAYMENT_TOKEN,
                need_email=True,
                send_email_to_provider=True,
                provider_data=json.dumps({
                    "receipt": {
                        "items": [
                            {
                                "description": "Подписка на генерацию персонального меню на 7 дней",
                                "quantity": 1,
                                "amount": {
                                    "value": float(SUBSCRIPTION_PRICE),
                                    "currency": "RUB"
                                },
                                "vat_code": 1,
                                "payment_mode": "full_payment",
                                "payment_subject": "service"
                            }
                        ],
                        "tax_system_code": 1
                    }
                })
            )
            
            await state.set_state(PaymentStates.waiting_for_payment)
            
        except Exception as e:
            await message.answer(
                "❌ Произошла ошибка при создании платежа. Попробуйте позже."
            )
            print(f"Ошибка создания платежа для меню: {e}")

@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout: PreCheckoutQuery):
    """Обработчик предварительной проверки платежа"""
    try:
        print(f"DEBUG: PreCheckoutQuery received - ID: {pre_checkout.id}, User: {pre_checkout.from_user.id}")
        
        # Быстро отвечаем OK (в течение 10 секунд)
        await pre_checkout.answer(ok=True)
        
        print(f"DEBUG: PreCheckoutQuery answered successfully - ID: {pre_checkout.id}")
        
    except Exception as e:
        print(f"ERROR: PreCheckoutQuery failed - ID: {pre_checkout.id}, Error: {e}")
        # В случае ошибки все равно отвечаем OK, чтобы не блокировать платеж
        try:
            await pre_checkout.answer(ok=True)
        except:
            pass

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, state: FSMContext):
    """Обработчик успешного платежа"""
    try:
        print(f"DEBUG: Successful payment received - User: {message.from_user.id}")
        print(f"DEBUG: Payment details: {message.successful_payment}")
        
        payment_id = message.successful_payment.invoice_payload
        print(f"DEBUG: Payment ID from payload: {payment_id}")
        
        # Подтверждаем платеж
        print(f"DEBUG: Calling PaymentManager.confirm_payment with ID: {payment_id}")
        success = await PaymentManager.confirm_payment(payment_id)
        print(f"DEBUG: PaymentManager.confirm_payment result: {success}")
        
        if success:
            # Получаем информацию о подписке
            async with async_session() as session:
                print(f"DEBUG: Searching for subscription with payment_id: {payment_id}")
                subscription = await session.execute(
                    select(Subscription).where(Subscription.payment_id == payment_id)
                )
                subscription = subscription.scalar_one_or_none()
                print(f"DEBUG: Found subscription: {subscription}")
                
                if subscription:
                    subscription_type = subscription.subscription_type
                    print(f"DEBUG: Subscription type: {subscription_type}")
                    
                    if subscription_type == 'diet_consultant':
                        await message.answer(
                            "🎉 <b>Подписка на личного диетолога активирована!</b>\n\n"
                            "Теперь вы можете задавать любые вопросы о питании и получать персональные рекомендации.\n\n"
                            "Просто напишите ваш вопрос, и я отвечу как ваш личный диетолог!\n\n"
                            "⏰ Подписка действует до: " + subscription.end_date.strftime("%d.%m.%Y"),
                            parse_mode="HTML"
                        )
                        print(f"DEBUG: Diet consultant subscription activated for user {message.from_user.id}")
                    elif subscription_type == 'menu_generator':
                        await message.answer(
                            "🎉 <b>Подписка на генерацию меню активирована!</b>\n\n"
                            "Теперь я могу создавать для вас персональное меню на любой период.\n\n"
                            "Просто напишите, на сколько дней вам нужно меню, и я его создам!\n\n"
                            "⏰ Подписка действует до: " + subscription.end_date.strftime("%d.%m.%Y"),
                            parse_mode="HTML"
                        )
                        print(f"DEBUG: Menu generator subscription activated for user {message.from_user.id}")
                    
                    await state.clear()
                    print(f"DEBUG: State cleared for user {message.from_user.id}")
                else:
                    print(f"ERROR: Subscription not found for payment_id: {payment_id}")
                    await message.answer("❌ Ошибка активации подписки. Обратитесь в поддержку.")
        else:
            print(f"ERROR: PaymentManager.confirm_payment returned False for payment_id: {payment_id}")
            await message.answer("❌ Ошибка подтверждения платежа. Обратитесь в поддержку.")
            
    except Exception as e:
        print(f"ERROR: Exception in successful_payment_handler: {e}")
        print(f"ERROR: Exception type: {type(e)}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        await message.answer("❌ Произошла ошибка при активации подписки. Обратитесь в поддержку.")

@router.message(Command("subscription"))
async def subscription_info_handler(message: Message):
    """Показывает информацию о подписках пользователя"""
    user_id = message.from_user.id
    
    try:
        # Проверяем подписки
        diet_subscription = await PaymentManager.get_subscription_info(user_id, 'diet_consultant')
        menu_subscription = await PaymentManager.get_subscription_info(user_id, 'menu_generator')
        
        response = "📋 <b>Ваши подписки:</b>\n\n"
        
        # Информация о подписке на диетолога
        if diet_subscription and diet_subscription['is_active']:
            response += f"👨‍⚕️ <b>Личный диетолог:</b> ✅ Активна\n"
            response += f"⏰ Осталось дней: {diet_subscription['days_left']}\n"
            response += f"📅 Действует до: {diet_subscription['end_date'].strftime('%d.%m.%Y')}\n\n"
        else:
            response += "👨‍⚕️ <b>Личный диетолог:</b> ❌ Неактивна\n"
            response += "💳 Для активации: /diet_consultant\n\n"
        
        # Информация о подписке на меню
        if menu_subscription and menu_subscription['is_active']:
            response += f"🍽️ <b>Генерация меню:</b> ✅ Активна\n"
            response += f"⏰ Осталось дней: {menu_subscription['days_left']}\n"
            response += f"📅 Действует до: {menu_subscription['end_date'].strftime('%d.%m.%Y')}\n\n"
        else:
            response += "🍽️ <b>Генерация меню:</b> ❌ Неактивна\n"
            response += "💳 Для активации: /menu_generator\n\n"
        
        await message.answer(response, parse_mode="HTML")
        
    except Exception as e:
        await message.answer("❌ Ошибка получения информации о подписках.")
        print(f"Ошибка получения информации о подписках: {e}")