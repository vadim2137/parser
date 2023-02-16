from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

domains = [
    ['PL', '🇵🇱', 'PL'],
    ['FR', '🇫🇷', 'FR'],
    ['AT', '🇦🇹', 'AT'],
    #['CZ', '🇨🇿', 'CZ'],
    #['BE', '🇧🇪', 'BE'],
    ['IT', '🇮🇹', 'IT'],
    ['LT', '🇱🇹', 'LT'],
    ['ES', '🇪🇸', 'ES'],
    # ['SK', '🇸🇰', 'SK'],
    ['PT', '🇵🇹', 'PT'],
    ['LU', '🇱🇺', 'LU'],
    ['NL', '🇳🇱', 'NL'],
    # ['HU', '🇭🇺', 'HU'],
    ['SE', '🇸🇪', 'SE'],
    ['DE', '🇩🇪', 'DE'],
    # ['CO.UK', '🇬🇧', 'GB'],
    ['COM', '🌍', 'US']
]


def domains_kb(is_auto_change=False):
    callback_text = 'domain'
    if is_auto_change:
        callback_text = 'auto_domain'

    markup = InlineKeyboardMarkup(row_width=2)
    for domain in domains:
        markup.insert(
            InlineKeyboardButton(
                text=f'VINTED.{domain[0]} {domain[1]}',
                callback_data=f'{callback_text}|{domain[0]}'
            )
        )

    if callback_text == 'auto_domain':
        markup.add(
            InlineKeyboardButton(
                text='🚫 Не использовать смену домена',
                callback_data=f'{callback_text}|False'
            )
        )
        markup.add(
            InlineKeyboardButton(
                text='❌ Отменить действие',
                callback_data='cancel'
            )
        )
    else:
        markup.add(
            InlineKeyboardButton(
                text='← Назад',
                callback_data='parser'
            )
        )

    return markup


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
