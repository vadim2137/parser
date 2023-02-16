from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import GROUP_ID

sub_chanel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=GROUP_ID,
                url=f'https://t.me/{GROUP_ID.split("@")[1]}'
            )
        ],
        [
            InlineKeyboardButton(
                text='✅ Я подписался',
                callback_data='back_to_start'
            )
        ]
    ]
)
