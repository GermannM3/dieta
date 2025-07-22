from aiogram import Router, F
from aiogram.types import Message, PreCheckoutQuery, LabeledPrice
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database.init_database import async_session, User
from sqlalchemy import select
from .payment_operations import PaymentManager
import os

router = Router()

# Состояния для FSM
class PaymentStates(StatesGroup):
    waiting_for_payment = State()

# Настройки платежей
YOOKASSA_PAYMENT_TOKEN = os.getenv('YOOKASSA_PAYMENT_TOKEN', '381764678:TEST:132209')
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
                provider_token=YOOKASSA_PAYMENT_TOKEN,
                currency="RUB",
                prices=[LabeledPrice(label="Подписка на 7 дней", amount=SUBSCRIPTION_PRICE * 100)]
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
                provider_token=YOOKASSA_PAYMENT_TOKEN,
                currency="RUB",
                prices=[LabeledPrice(label="Подписка на 7 дней", amount=SUBSCRIPTION_PRICE * 100)]
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
    await pre_checkout.answer(ok=True)

@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, state: FSMContext):
    """Обработчик успешного платежа"""
    payment_id = message.successful_payment.invoice_payload
    
    try:
        # Подтверждаем платеж
        success = await PaymentManager.confirm_payment(payment_id)
        
        if success:
            # Получаем информацию о подписке
            async with async_session() as session:
                subscription = await session.execute(
                    select(Subscription).where(Subscription.payment_id == payment_id)
                )
                subscription = subscription.scalar_one_or_none()
                
                if subscription:
                    subscription_type = subscription.subscription_type
                    
                    if subscription_type == 'diet_consultant':
                        await message.answer(
                            "🎉 <b>Подписка на личного диетолога активирована!</b>\n\n"
                            "Теперь вы можете задавать любые вопросы о питании и получать персональные рекомендации.\n\n"
                            "Просто напишите ваш вопрос, и я отвечу как ваш личный диетолог!\n\n"
                            "⏰ Подписка действует до: " + subscription.end_date.strftime("%d.%m.%Y"),
                            parse_mode="HTML"
                        )
                    elif subscription_type == 'menu_generator':
                        await message.answer(
                            "🎉 <b>Подписка на генерацию меню активирована!</b>\n\n"
                            "Теперь я могу создавать для вас персональное меню на любой период.\n\n"
                            "Просто напишите, на сколько дней вам нужно меню, и я его создам!\n\n"
                            "⏰ Подписка действует до: " + subscription.end_date.strftime("%d.%m.%Y"),
                            parse_mode="HTML"
                        )
                    
                    await state.clear()
                else:
                    await message.answer("❌ Ошибка активации подписки. Обратитесь в поддержку.")
        else:
            await message.answer("❌ Ошибка подтверждения платежа. Обратитесь в поддержку.")
            
    except Exception as e:
        await message.answer("❌ Произошла ошибка при активации подписки. Обратитесь в поддержку.")
        print(f"Ошибка обработки успешного платежа: {e}")

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