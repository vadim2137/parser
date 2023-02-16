from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

wl_categories_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Мода и Одежда',
                callback_data='wl_category|12465'
            ),
            InlineKeyboardButton(
                text='Моб. устройства',
                callback_data='wl_category|16000'
            ),
            InlineKeyboardButton(
                text='Детские товары',
                callback_data='wl_category|12461'
            )
        ],
        [
            InlineKeyboardButton(
                text='Электроника',
                callback_data='wl_category|15000'
            ),
            InlineKeyboardButton(
                text='Спорт',
                callback_data='wl_category|12579'
            ),
            InlineKeyboardButton(
                text='Велосипеды',
                callback_data='wl_category|17000'
            )
        ],
        [
            InlineKeyboardButton(
                text='Видеоигры',
                callback_data='wl_category|16000'
            ),
            InlineKeyboardButton(
                text='Мебель',
                callback_data='wl_category|12467'
            ),
            InlineKeyboardButton(
                text='Бытовая техника',
                callback_data='wl_category|13100'
            )
        ],
        [
            InlineKeyboardButton(
                text='Мотокоплектующие',
                callback_data='wl_category|14000'
            ),
            InlineKeyboardButton(
                text='🔸 Все категории',
                callback_data='wl_category|all'
            ),
            InlineKeyboardButton(
                text='ТВ, Аудио, Фотокамеры',
                callback_data='wl_category|12545'
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
