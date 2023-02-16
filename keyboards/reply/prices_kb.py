from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

prices_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='1-250'),
            KeyboardButton(text='1-500'),
            KeyboardButton(text=' 1-1500')
        ]
    ],
    resize_keyboard=True
)
