from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def teams_kb(teams: list):
    markup = InlineKeyboardMarkup()
    for team in teams:
        markup.add(
            InlineKeyboardButton(
                text=f'{team.team_name}',
                callback_data=f'team|{team.id}'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='➕ Добавить тиму',
            callback_data='new_team'
        )
    )
    markup.add(
        InlineKeyboardButton(
            text='← Назад',
            callback_data='admin'
        )
    )
    return markup


def team_kb(team_id: int):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='❌ Удалить тиму',
                    callback_data=f'del_team|{team_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='← Назад',
                    callback_data='team_ref'
                )
            ]
        ]
    )
    return markup


back_to_teams = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='← Назад',
                callback_data='team_ref'
            )
        ]
    ]
)
