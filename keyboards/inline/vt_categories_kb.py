from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

category_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='👦 Детское',
                callback_data='link_category|catalog[]=1193'
            ),
            InlineKeyboardButton(
                text='🏠 Дом и сад',
                callback_data='link_category|catalog[]=1918'
            )
        ],
        [
            InlineKeyboardButton(
                text='🚻 Мужская/Женская одежда',
                callback_data='link_category|catalog[]=1904&catalog[]=5'
            )
        ],
        [
            InlineKeyboardButton(
                text='❌ Отменить действие',
                callback_data='cancel'
            )
        ]
    ]
)
