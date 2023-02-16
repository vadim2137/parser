from datetime import datetime, timedelta, date

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_dates():
    date_format = '%Y-%m-%d'
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    after_yesterday = today - timedelta(days=2)
    return {
        'today': today.strftime(date_format),
        'yesterday': yesterday.strftime(date_format),
        'after_yesterday': after_yesterday.strftime(date_format)
    }


def dates_kb():
    dates = get_dates()
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=dates['after_yesterday']),
                KeyboardButton(text=dates['yesterday'])
            ],
            [
                KeyboardButton(text=dates['today'])
            ]
        ],
        resize_keyboard=True
    )
    return keyboard
