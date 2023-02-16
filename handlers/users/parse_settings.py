import operator

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from data.config import photo_1
from keyboards import settings_kb, back_to_settings_kb
from loader import dp
from states import PostsFilter
from utils import anti_flood
from utils.schemas import LogFilter
from utils.db_commands import update_log_filter, select_log_filter, update_posts_filter


@dp.callback_query_handler(Text(equals='settings'), state='*')
@dp.throttled(anti_flood, rate=2)
async def parse_settings(call: types.CallbackQuery, state: FSMContext):
    filter = await select_log_filter(call.from_user.id)
    await call.message.edit_caption(
        caption='<b>🛠 Настройки</b>\n\n'
                '🟢 — Включено\n'
                '🔴 — Отключено',
        reply_markup=settings_kb(
            filter.photo,
            filter.name,
            filter.price,
            filter.location,
            filter.title,
            filter.post_date,
            filter.count_posts,
            filter.viewed_posts
        )
    )
    await state.reset_state(with_data=False)


@dp.callback_query_handler(Text(startswith='filter'), state='*')
@dp.throttled(anti_flood, rate=0.5)
async def log_filter(call: types.CallbackQuery):
    await update_log_filter(
        call.from_user.id,
        False if call.data.split('|')[2] == 'True' else True,
        operator.attrgetter(call.data.split('|')[1])(LogFilter)
    )
    filter = await select_log_filter(call.from_user.id)
    await call.message.edit_reply_markup(
        settings_kb(
            filter.photo,
            filter.name,
            filter.price,
            filter.location,
            filter.title,
            filter.post_date,
            filter.count_posts,
            filter.viewed_posts
        )
    )


@dp.callback_query_handler(Text(equals='posts_filter'), state='*')
@dp.throttled(anti_flood, rate=2)
async def posts_filter(call: types.CallbackQuery):
    filter = await select_log_filter(call.from_user.id)
    await call.message.edit_caption(
        f'<b>🫣 Кол-во объявлений для выдачи</b>\n'
        f'Ваш фильтр: <b>{filter.posts_filter}</b>\n\n'
        f'— При успешном достижении установленного Вами '
        f'количества объявлений - парсер остановиться\n\n'
        f'<b>💡 Введите максимальное кол-во объявлений для выдачи [Max: 50]</b>',
        reply_markup=back_to_settings_kb
    )
    await PostsFilter.filter.set()


@dp.message_handler(state=PostsFilter.filter)
@dp.throttled(anti_flood, rate=2)
async def change_posts_filter(message: types.Message, state: FSMContext):
    try:
        if 50 >= int(message.text) > 0:
            await update_posts_filter(message.from_user.id, int(message.text))
            filter = await select_log_filter(message.from_user.id)
            await message.answer_photo(
                photo=photo_1,
                caption=f'<b>🫣 Кол-во объявлений для выдачи</b>\n'
                        f'Ваш фильтр: <b>{filter.posts_filter}</b>',
                reply_markup=back_to_settings_kb
            )
        else:
            await message.answer(
                '<b>🚫 Максимум 50 объявлений!</b>'
            )
    except ValueError:
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )

    await state.reset_state(with_data=False)
