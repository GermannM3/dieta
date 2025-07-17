from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Профиль'), KeyboardButton(text='Добавить еду')],
        [KeyboardButton(text='История приёмов пищи'), KeyboardButton(text='Мои шаблоны')],
        [KeyboardButton(text='Трекер воды'), KeyboardButton(text='Трекер настроения')],
        [KeyboardButton(text='Трекер жировой массы'), KeyboardButton(text='Баллы и прогресс')],
        [KeyboardButton(text='Сгенерировать меню'), KeyboardButton(text='Личный диетолог')],
        [KeyboardButton(text='Статистика'), KeyboardButton(text='Распознать еду на фото')],
    ],
    resize_keyboard=True
)

# Клавиатура "Назад" для возврата в главное меню
back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='back')]
    ]
)

# Клавиатура профиля с кнопкой редактирования
profile_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='✏️ Редактировать профиль', callback_data='edit_profile')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='back')]
    ]
)

# Клавиатура для старта диалога
start_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Начать диалог', callback_data='start_dialog')]
    ]
)

# Клавиатура для добавления еды с кнопкой шаблонов
add_food_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='🍽️ Выбрать из шаблонов', callback_data='food_templates')],
        [InlineKeyboardButton(text='➕ Создать шаблон', callback_data='create_template_from_addmeal')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='back')]
    ]
)

# Клавиатура для трекинга жира
fat_tracker_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='📏 Новое измерение', callback_data='fat_new_measurement')],
        [InlineKeyboardButton(text='📊 История измерений', callback_data='fat_history')],
        [InlineKeyboardButton(text='🎯 Установить цель', callback_data='fat_set_goal')],
        [InlineKeyboardButton(text='💡 Получить рекомендации', callback_data='fat_recommendations')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='back')]
    ]
)

# Клавиатура для подтверждения данных
fat_confirm_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='✅ Сохранить', callback_data='fat_save')],
        [InlineKeyboardButton(text='🔄 Повторить измерение', callback_data='fat_restart')],
        [InlineKeyboardButton(text='❌ Отмена', callback_data='back')]
    ]
)

# Клавиатура для создания шаблонов (когда их нет)
create_template_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='➕ Добавить шаблон', callback_data='create_template')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='back')]
    ]
)
