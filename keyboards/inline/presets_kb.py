from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db_commands import select_vt_presets, select_jg_presets, select_wl_presets


# Vinted
def start_vt_preset_kb(preset_id: str):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text='👾 Да', callback_data=f'use_vt_preset|{preset_id}|background'))
    markup.row(InlineKeyboardButton(
        text='🌐 В стандартном режиме', callback_data=f'use_vt_preset|{preset_id}|standard'
    ))
    markup.row(InlineKeyboardButton(text='❌ Отменить действие', callback_data='cancel'))
    return markup


start_vt_without_preset = InlineKeyboardMarkup()
start_vt_without_preset.row(InlineKeyboardButton(text='👾 Да', callback_data=f'start_vinted|background'))
start_vt_without_preset.row(InlineKeyboardButton(
    text='🌐 В стандартном режиме', callback_data=f'start_vinted|standard'
))
start_vt_without_preset.row(InlineKeyboardButton(text='❌ Отменить действие', callback_data='cancel'))

enable_registration_kb = InlineKeyboardMarkup()
enable_registration_kb.row(InlineKeyboardButton(text='✅ Да', callback_data='enable_registration|yes'))
enable_registration_kb.insert(InlineKeyboardButton(text='❌ Нет', callback_data='enable_registration|no/'))

use_vt_presets_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='✅ Да',
                callback_data='choose_vt_preset|yes'
            ),
            InlineKeyboardButton(
                text='❌ Нет',
                callback_data='choose_vt_preset|no'
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

vt_presets_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='✅ Да',
                callback_data='add_vt_preset'
            ),
            InlineKeyboardButton(
                text='❌ Нет',
                callback_data='start_vt_without_presets'
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


def use_one_vt_preset_kb(preset_id: int, date: bool):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text='🌐 Стандартный', callback_data=f'use_vt_preset|{preset_id}|standard'))
    markup.insert(InlineKeyboardButton(text='👾 Фоновый', callback_data=f'pre_vt_preset|{preset_id}|background'))
    if date:
        markup.row(InlineKeyboardButton(text='📅 Установить дату', callback_data=f'set_vt_date|{preset_id}'))
    markup.row(InlineKeyboardButton(text='❌ Удалить', callback_data=f'del_vt_preset|{preset_id}'))
    markup.insert(InlineKeyboardButton(text='← Назад', callback_data='choose_vt_preset|yes'))
    return markup


quit_vt_date = InlineKeyboardMarkup()
quit_vt_date.add(
    InlineKeyboardButton(
        text='← Выйти',
        callback_data='quit_vt_date'
    )
)

start_vt_parser_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🌐️ Стандартный',
                callback_data='start_vinted|standard'
            ),
            InlineKeyboardButton(
                text='👾️ Фоновый',
                callback_data='pre_start_vinted|background'
            ),
        ],
        [
            InlineKeyboardButton(
                text='❌ Отменить действие',
                callback_data='cancel'
            )
        ]
    ]
)


async def vt_presets_list(user_id: int):
    vt_presets = await select_vt_presets(user_id)
    markup = InlineKeyboardMarkup()
    for preset in vt_presets:
        markup.add(
            InlineKeyboardButton(
                text=preset.preset_name,
                callback_data=f'start_vt_preset|{preset.id}'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='❌ Отменить действие',
            callback_data='cancel'
        )
    )

    return markup


# Wallapop
def start_wl_preset_kb(preset_id: str):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text='👾 Да', callback_data=f'use_wl_preset|{preset_id}|background'))
    markup.row(InlineKeyboardButton(
        text='🌐 В стандартном режиме', callback_data=f'use_wl_preset|{preset_id}|standard'
    ))
    markup.row(InlineKeyboardButton(text='❌ Отменить действие', callback_data='cancel'))
    return markup


start_wl_without_preset = InlineKeyboardMarkup()
start_wl_without_preset.row(InlineKeyboardButton(text='👾 Да', callback_data=f'start_wallapop|background'))
start_wl_without_preset.row(InlineKeyboardButton(
    text='🌐 В стандартном режиме', callback_data=f'start_wallapop|standard'
))
start_wl_without_preset.row(InlineKeyboardButton(text='❌ Отменить действие', callback_data='cancel'))

use_wl_presets_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='✅ Да',
                callback_data='choose_wl_preset|yes'
            ),
            InlineKeyboardButton(
                text='❌ Нет',
                callback_data='choose_wl_preset|no'
            )
        ],
        [
            InlineKeyboardButton(
                text='⬅ Назад',
                callback_data='parser'
            )
        ]
    ]
)


def use_one_wl_preset_kb(preset_id: int, date: bool):
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton(text='🌐 Стандартный', callback_data=f'use_wl_preset|{preset_id}|standard'))
    markup.insert(InlineKeyboardButton(text='👾 Фоновый', callback_data=f'pre_wl_preset|{preset_id}|background'))
    markup.add(InlineKeyboardButton(text='❌ Удалить', callback_data=f'del_wl_preset|{preset_id}'))
    if date:
        markup.row(InlineKeyboardButton(text='📅 Установить дату', callback_data=f'set_wl_date|{preset_id}'))
    markup.row(InlineKeyboardButton(text='← Назад', callback_data='choose_wl_preset|yes'))
    return markup


quit_wl_date = InlineKeyboardMarkup()
quit_wl_date.add(
    InlineKeyboardButton(
        text='← Выйти',
        callback_data='quit_wl_date'
    )
)

wl_presets_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='✅ Да',
                callback_data='add_wl_preset'
            ),
            InlineKeyboardButton(
                text='❌ Нет',
                callback_data='start_wl_without_presets'
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

start_wl_parser_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='🌐 Стандартный',
                callback_data='start_wallapop|standard'
            ),
            InlineKeyboardButton(
                text='👾️ Фоновый',
                callback_data='pre_start_wallapop|background'
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


async def wl_presets_list(user_id: int):
    vt_presets = await select_wl_presets(user_id)
    markup = InlineKeyboardMarkup()
    for preset in vt_presets:
        markup.add(
            InlineKeyboardButton(
                text=preset.preset_name,
                callback_data=f'start_wl_preset|{preset.id}'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='❌ Отменить действие',
            callback_data='cancel'
        )
    )

    return markup


# Jofogas
use_jg_presets_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='✅ Да',
                callback_data='choose_jg_preset|yes'
            ),
            InlineKeyboardButton(
                text='❌ Нет',
                callback_data='choose_jg_preset|no'
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

jg_presets_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='✅ Да',
                callback_data='add_jg_preset'
            ),
            InlineKeyboardButton(
                text='❌ Нет',
                callback_data='start_jg_without_presets'
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


def use_one_jg_preset_kb(preset_id: int):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='✅ Использовать',
                    callback_data=f'use_jg_preset|{preset_id}'
                ),
                InlineKeyboardButton(
                    text='❌ Удалить',
                    callback_data=f'del_jg_preset|{preset_id}'
                )
            ],
            [
                InlineKeyboardButton(
                    text='← Назад',
                    callback_data='choose_jg_preset|yes'
                )
            ]
        ]
    )
    return markup


start_jg_parser_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='⚡️ Запустить',
                callback_data='start_jofogas'
            ),
            InlineKeyboardButton(
                text='❌ Отменить действие',
                callback_data='cancel'
            )
        ]
    ]
)


async def jg_presets_list(user_id: int):
    jg_presets = await select_jg_presets(user_id)
    markup = InlineKeyboardMarkup()
    for preset in jg_presets:
        markup.add(
            InlineKeyboardButton(
                text=preset.preset_name,
                callback_data=f'start_jg_preset|{preset.id}'
            )
        )
    markup.add(
        InlineKeyboardButton(
            text='❌ Отменить действие',
            callback_data='cancel'
        )
    )

    return markup
