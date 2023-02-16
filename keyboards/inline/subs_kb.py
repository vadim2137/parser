import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import sub_tariffs


def subs_kb(service: str):
    markup = InlineKeyboardMarkup()
    for tariff in sub_tariffs[service].items():
        days = str(datetime.timedelta(hours=tariff[0])).replace('days', 'дней').replace('day', 'день')
        markup.add(
            InlineKeyboardButton(
                text=f'{days.split(",")[0]} [ {tariff[1][0]} $ ≈ {tariff[1][1]} ₽ ]',
                callback_data=f'sub|{tariff[0]}|{service}'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='← Назад',
            callback_data='parser'
        )
    )
    return markup
