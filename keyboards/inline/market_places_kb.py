from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

market_places_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🌎 VINTED',
                callback_data='vinted'
            ),
            InlineKeyboardButton(
                text='🇪🇺 WALLAPOP',
                callback_data='wallapop'
            )
        ],
        [
            InlineKeyboardButton(
                text='🔎 Последний поиск',
                callback_data='last_search'
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

wl_domains = [
    ['ES', '🇪🇸'],
    ['FR', '🇫🇷'],
    ['PT', '🇵🇹'],
    ['IT', '🇮🇹']
]


def wallapop_kb():
    markup = InlineKeyboardMarkup(row_width=2)
    for domain in wl_domains:
        markup.insert(
            InlineKeyboardButton(
                text=f'{domain[1]} {domain[0]}.WALLAPOP.COM',
                callback_data=f'open_wl_{domain[0]}|{domain[1]}'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='⬅ Назад',
            callback_data='parser'
        )
    )
    return markup
