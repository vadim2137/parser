from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

stop_parser_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='⛔️ Остановить парсер')
        ]
    ],
    resize_keyboard=True
)
