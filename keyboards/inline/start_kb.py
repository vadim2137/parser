from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import ADMINS_ID


def start_kb(user_id: int):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='⚡️ Парсер', callback_data='parser'),
            ],
            [
                InlineKeyboardButton(text='💵 Пополнить баланс', callback_data='add_balance'),
                InlineKeyboardButton(text='⚙️ Настройки', callback_data='settings')
            ],
            [
                InlineKeyboardButton(text='🤝 Реферальная система', callback_data='referal')
            ],
            [
                InlineKeyboardButton(text='💌 Помощь', callback_data='help')
            ]
        ]
    )
    if user_id in ADMINS_ID:
        markup.add(
            InlineKeyboardButton(
                text='😎 Админ меню',
                callback_data='admin'
            )
        )
    return markup


user_agreement_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🧾 Пользовательское соглашение',
                url='https://telegra.ph/Polzovatelskoe-soglashenie-10-29-3'
            )
        ],
        [
            InlineKeyboardButton(
                text='✅ Я ознакомлен',
                callback_data='back_to_start'
            )
        ]
    ]
)


back_to_start_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='← Назад',
                callback_data='back_to_start'
            )
        ]
    ]
)


back_to_parser_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='← Назад',
                callback_data='parser'
            )
        ]
    ]
)

back_to_add_balance_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='← Назад',
                callback_data='add_balance'
            )
        ]
    ]
)
