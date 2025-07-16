from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, Message, PreCheckoutQuery

from components.payment_system.payment_btn import payment_kb
from components.payment_system.payment_operations import add_premium


router = Router()


@router.message(Command('premium'))
async def premium(message: Message):
    prices = [LabeledPrice(label='XTR', amount=100)]  
    await message.answer_invoice(  
        title='VIP AI',  
        description=f'Премиум подписка дает доступ к обработке изображений. Стоимость 100 звезд на 30 дней',  
        prices=prices,   
        provider_token='',
        payload='premium',  
        currency='XTR', 
        reply_markup=payment_kb 
    )

@router.pre_checkout_query()
async def checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def star_payment(message: Message):
    await message.answer(text='<b>Спасибо за оформление подписки!🤗</b>')
    await add_premium(tg_id=str(message.from_user.id))