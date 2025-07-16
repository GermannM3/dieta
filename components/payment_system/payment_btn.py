from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


payment_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оплатить⭐️', pay=True)]
])