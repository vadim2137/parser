from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

payment_methods_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='⚜️ CryptoBot',
                callback_data='crypto_bot'
            )
        ],
        [
            InlineKeyboardButton(
                text='⬅ Назад',
                callback_data='back_to_start'
            )
        ]
    ]
)


def crypto_bot_currencies_kb():
    currencies = ['USDT', 'BUSD', 'USDC', 'BTC', 'ETH', 'TON', 'BNB']
    markup = InlineKeyboardMarkup(row_width=3)
    for currency in currencies:
        markup.insert(
            InlineKeyboardButton(
                text=currency,
                callback_data=f'crypto_bot_currency|{currency}'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='❌ Отменить действие',
            callback_data='cancel'
        )
    )
    return markup


def check_crypto_bot_kb(url: str, invoice_hash: int):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🔗 Оплатить',
                    url=url
                )
            ],
            [
                InlineKeyboardButton(
                    text='♻️ Проверить оплату',
                    callback_data=f'check_crypto_bot|{invoice_hash}'
                )
            ]
        ]
    )
    return markup


back_to_add_balance_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='⬅ Назад',
                callback_data='add_balance'
            )
        ]
    ]
)
