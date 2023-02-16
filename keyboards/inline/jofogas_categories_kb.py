from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

jg_categories_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='👦 Детское',
                callback_data='jg_category|baba-mama'
            ),
            InlineKeyboardButton(
                text='🛠 Услуги',
                callback_data='jg_category|uzlet-szolgaltatas'
            ),
            InlineKeyboardButton(
                text='⚽️ Спорт',
                callback_data='jg_category|szabadido-sport'
            )
        ],
        [
            InlineKeyboardButton(
                text='🎽 Одежда',
                callback_data='jg_category|divat-ruhazat'
            ),
            InlineKeyboardButton(
                text='📱 Электроника',
                callback_data='jg_category|muszaki-cikkek-elektronika'
            ),
            InlineKeyboardButton(
                text='🏠 Дом',
                callback_data='jg_category|otthon-haztartas'
            )
        ],
        [
            InlineKeyboardButton(
                text='← Назад',
                callback_data='parser'
            )
        ]
    ]
)
