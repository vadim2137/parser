from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def settings_kb(
        photo: bool,
        name: bool,
        price: bool,
        location: bool,
        title: bool,
        post_date: bool,
        count_posts: bool,
        viewed_posts: bool
):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='🔻 Конфигурация лога',
                    callback_data='echo'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🟢 Фото' if photo else '🔴 Фото',
                    callback_data=f'filter|photo|{photo}'
                ),
                InlineKeyboardButton(
                    text='🟢 Имя' if name else '🔴 Имя',
                    callback_data=f'filter|name|{name}'
                ),
                InlineKeyboardButton(
                    text='🟢 Цена' if price else '🔴 Цена',
                    callback_data=f'filter|price|{price}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🟢 Локация' if location else '🔴 Локация',
                    callback_data=f'filter|location|{location}'
                ),
                InlineKeyboardButton(
                    text='🟢 Название товара' if title else '🔴 Название товара',
                    callback_data=f'filter|title|{title}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🔻 Отображение фильтров',
                    callback_data='echo'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🟢 Дата публикации' if post_date else '🔴 Дата публикации',
                    callback_data=f'filter|post_date|{post_date}'
                ),
                InlineKeyboardButton(
                    text='🟢 Кол-во объявлений' if count_posts else '🔴 Кол-во объявлений',
                    callback_data=f'filter|count_posts|{count_posts}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🔻 Модификации',
                    callback_data='echo'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🟢 Только непросмотренные объявления' if viewed_posts else
                    '🔴 Только непросмотренные объявления',
                    callback_data=f'filter|viewed_posts|{viewed_posts}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='🫣 Кол-во объявлений для выдачи',
                    callback_data='posts_filter'
                )
            ]
        ]
    )
    markup.add(
        InlineKeyboardButton(
            text='← Назад',
            callback_data='back_to_start'
        )
    )
    return markup


back_to_settings_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='← Назад',
                callback_data='settings')
        ]
    ]
)
