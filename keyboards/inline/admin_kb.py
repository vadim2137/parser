from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

callback_interact = CallbackData('interact', 'action', 'user_id', 'is_banned')

admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='💌 Рассылка',
                callback_data='mail'
            ),
            InlineKeyboardButton(
                text='📊️ Статистика',
                callback_data='stata'
            )
        ],
        [
            InlineKeyboardButton(
                text='🤝 Реф. для тим',
                callback_data='team_ref'
            )
        ],
        [
            InlineKeyboardButton(
                text='← Назад',
                callback_data='back_to_start'
            )
        ]
    ]
)


def interact_user(user_id: int, is_banned: bool):
    keyboard = InlineKeyboardMarkup()
    if is_banned:
        keyboard.row(InlineKeyboardButton(
            text='🛠 Разблокировать', callback_data=callback_interact.new('ban', user_id, int(is_banned))
        ))
    else:
        keyboard.row(InlineKeyboardButton(
            text='⚒ Заблокировать', callback_data=callback_interact.new('unban', user_id, int(is_banned))
        ))
    keyboard.row(InlineKeyboardButton(
        text='✖️ Удалить', callback_data=callback_interact.new('delete', user_id, int(is_banned))
    ))
    return keyboard


back_to_admin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='← Назад',
                callback_data='back_to_admin_menu'
            )
        ]
    ]
)

cancel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='❌ Отменить действие',
                callback_data='cancel'
            )
        ]
    ]
)
