import random
import time
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove

from keyboards import cancel_kb, count_posts_kb, prices_kb, jg_categories_kb, subs_kb, count_reviews_kb
from keyboards.inline.presets_kb import use_jg_presets_kb, jg_presets_list, \
    use_one_jg_preset_kb, jg_presets_kb, start_jg_parser_kb
from keyboards.reply.dates_kb import dates_kb
from loader import dp
from states import JGParser
from utils import anti_flood
from utils.db_commands import select_log_filter, select_jg_preset_by_id, \
    delete_jg_preset, select_count_jg_presets, add_jg_preset, select_all_subs
from utils.start_parse_jg import parse_jofogas


@dp.callback_query_handler(Text(equals='jofogas'), state='*')
@dp.throttled(anti_flood, rate=2)
async def jofogas(call: types.CallbackQuery, state: FSMContext):
    subs = [sub.service for sub in await select_all_subs(call.from_user.id)]
    if '🇭🇺 JOFOGAS' in subs:
        await state.update_data(vt_work=False, wl_work=False, jg_work=False)
        count_jg_presets = await select_count_jg_presets(call.from_user.id)

        if count_jg_presets > 0:
            await call.message.edit_caption(
                '<b>🔎 Вы выбрали JOFOGAS 🇭🇺</b>\n'
                '<b>🗂 Использовать пресеты?</b>',
                reply_markup=use_jg_presets_kb
            )
            await JGParser.use_presets.set()
        else:
            await call.message.edit_caption(
                '<b>🔎 Вы выбрали JOFOGAS 🇭🇺</b>\n'
                f'<b>🗄 Выберите нужную категорию по которой будет производиться парсинг:</b>\n',
                reply_markup=jg_categories_kb
            )
            await JGParser.category.set()
    else:
        await call.message.edit_caption(
            '<b>❗️ Отсутствует подписка на JOFOGAS 🇭🇺</b>\n'
            '<b>⭐️ Тарифы на подписку:</b>',
            reply_markup=subs_kb('🇭🇺 JOFOGAS')
        )


@dp.callback_query_handler(Text(startswith='choose_jg_preset'), state=JGParser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def choose_jg_preset(call: types.CallbackQuery):
    if call.data.split('|')[1] == 'yes':
        await call.message.edit_caption(
            '<b>🗂 Выберите пресет из списка:</b>',
            reply_markup=await jg_presets_list(call.from_user.id)

        )
    else:
        await call.message.edit_caption(
            f'<b>🗄 Выберите нужную категорию по которой будет производиться парсинг:</b>\n',
            reply_markup=jg_categories_kb
        )
        await JGParser.category.set()


@dp.callback_query_handler(Text(startswith='start_jg_preset'), state=JGParser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def start_jg_preset(call: types.CallbackQuery):
    jg_preset = await select_jg_preset_by_id(int(call.data.split('|')[1]))

    await call.message.edit_caption(
        f'<b>🗂 Пресет: <code>{jg_preset.preset_name}</code></b>\n\n'
        f'<b>Фильтры:</b>\n'
        f'📅 Дата публикации: <b>{jg_preset.parse_date_str}</b>\n'
        f'⭐ Кол-во отзывов: <b>{jg_preset.count_reviews}</b>\n'
        f'⌨️ Ссылка: {jg_preset.url}\n\n'
        f'<b>❓ Использовать пресет?</b>',
        reply_markup=use_one_jg_preset_kb(jg_preset.id)
    )


@dp.callback_query_handler(Text(startswith='use_jg_preset'), state=JGParser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def use_one_jg_preset(call: types.CallbackQuery, state: FSMContext):
    subs = [sub.service for sub in await select_all_subs(call.from_user.id)]
    if '🇭🇺 JOFOGAS' in subs:
        jg_preset = await select_jg_preset_by_id(int(call.data.split('|')[1]))
        await state.update_data(
            jg_category=jg_preset.category,
            jg_url=jg_preset.url,
            jg_search_text=jg_preset.search_text,
            jg_parse_date=jg_preset.parse_date,
            jg_parse_date_str=jg_preset.parse_date_str,
            jg_rating_count=jg_preset.count_reviews,
            jg_from_price=jg_preset.from_price,
            jg_to_price=jg_preset.to_price,
            jg_from_page=jg_preset.from_page,
            jg_to_page=jg_preset.to_page
        )
        await parse_jofogas(call, state)
    else:
        await call.message.edit_caption(
            '<b>❗️ Отсутствует подписка на JOFOGAS 🇭🇺</b>\n'
            '<b>⭐️ Тарифы на подписку:</b>',
            reply_markup=subs_kb('🇭🇺 JOFOGAS')
        )


@dp.callback_query_handler(Text(startswith='del_jg_preset'), state=JGParser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def del_one_jg_preset(call: types.CallbackQuery):
    await delete_jg_preset(int(call.data.split('|')[1]))
    await call.answer(
        '❌ Пресет удалён!'
    )
    count_jg_presets = await select_count_jg_presets(call.from_user.id)

    if count_jg_presets > 0:
        await call.message.edit_caption(
            '<b>🔎 Вы выбрали JOFOGAS 🇭🇺</b>\n'
            '<b>🗂 Выберите пресет из списка:</b>',
            reply_markup=await jg_presets_list(call.from_user.id)
        )
    else:
        await call.message.edit_caption(
            f'<b>🗄 Выберите нужную категорию по которой будет производиться парсинг:</b>\n',
            reply_markup=jg_categories_kb
        )
        await JGParser.category.set()


@dp.callback_query_handler(text_startswith='jg_category', state=JGParser.category)
@dp.throttled(anti_flood, rate=2)
async def choose_category_by_btn_jg(call: types.CallbackQuery, state: FSMContext):
    category = call.data.split('|')[1]
    await state.update_data(
        jg_url=f'https://www.jofogas.hu/magyarorszag?{category}',
        jg_category=category,
        jg_search_text=''
    )

    filter = await select_log_filter(call.from_user.id)
    if not filter.post_date:
        date = str(datetime.today().date()).split('-')
        dt = datetime(int(date[0]), int(date[1]), int(date[2]))
        await state.update_data(
            jg_parse_date=time.mktime(dt.timetuple()),
            jg_parse_date_str=datetime.today().date()
        )
        if not filter.count_posts:
            await state.update_data(jg_count_posts=random.randint(10, 30))
            await call.message.answer('🔍', reply_markup=count_reviews_kb())
            await call.message.answer(
                '<i><b>🔍 Введите максимально допустимое</b> количество отзывов <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await JGParser.count_reviews.set()
        else:
            await call.message.answer('🔍', reply_markup=count_posts_kb())
            await call.message.answer(
                '<i><b>📦 Введите максимально допустимое</b> количество активных объявлений <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await JGParser.count_posts.set()

    else:
        await call.message.answer('🔍', reply_markup=dates_kb())
        await call.message.answer(
            '<i><b>📅 Введите минимальную</b> дату публикации <b>товара на сайте</b></i>\n'
            '<i>Пример: 2022-09-22</i>',
            reply_markup=cancel_kb
        )

        await JGParser.date.set()


@dp.message_handler(state=JGParser.date)
@dp.throttled(anti_flood, rate=2)
async def get_count_posts(message: types.Message, state: FSMContext):
    try:
        date = message.text.split('-')
        dt = datetime(int(date[0]), int(date[1]), int(date[2]))
        await state.update_data(
            jg_parse_date=time.mktime(dt.timetuple()),
            jg_parse_date_str=message.text
        )

        await message.answer('🔍', reply_markup=count_reviews_kb())
        await message.answer(
            '<i><b>⭐️ Введите максимально допустимое</b> количество отзывов <b>у продавца</b></i>\n'
            '<i>Пример: 5</i>',
            reply_markup=cancel_kb
        )

        await JGParser.count_reviews.set()

    except (ValueError, IndexError):
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=JGParser.count_reviews)
@dp.throttled(anti_flood, rate=2)
async def get_count_reviews(message: types.Message, state: FSMContext):
    try:
        await state.update_data(jg_rating_count=int(message.text))
        await message.answer('🔍', reply_markup=prices_kb)
        await message.answer(
            '<b>💵 Введите диапазон стоимости товара</b>\n'
            '<i>Пример: 1-1000</i>',
            reply_markup=cancel_kb
        )

        await JGParser.price.set()
    except ValueError:
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=JGParser.price)
@dp.throttled(anti_flood, rate=2)
async def get_from_page(message: types.Message, state: FSMContext):
    try:
        await state.update_data(
            jg_from_price=int(message.text.split('-')[0]),
            jg_to_price=int(message.text.split('-')[1])
        )
        await message.answer('🔍', reply_markup=ReplyKeyboardRemove())
        await message.answer(
            '<b>🔍 С какой страницы начать парсинг?</b>\n'
            '<i>Пример: 3</i>',
            reply_markup=cancel_kb
        )
        await JGParser.from_page.set()
    except (IndexError, ValueError):
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=JGParser.from_page)
@dp.throttled(anti_flood, rate=2)
async def get_to_page(message: types.Message, state: FSMContext):
    try:
        await state.update_data(jg_from_page=int(message.text))
        await message.answer(
            '<b>🔍 По какую страницу парсить?</b>\n'
            '<i>Пример: 20 [MAX: 20]</i>',
            reply_markup=cancel_kb
        )

        await JGParser.to_page.set()
    except ValueError:
        await message.answer('<i><b>❗️ Введите данные в правильном формате!</b></i>')


@dp.message_handler(state=JGParser.to_page)
@dp.throttled(anti_flood, rate=2)
async def use_presets_jg(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        if int(message.text) > data['jg_from_page']:
            if int(message.text) - data['jg_from_page'] + 1 > 20:
                await message.answer(
                    '<b>❗️ Должно быть максимум 20 страниц для парсинга!</b>'
                )
            else:
                await state.update_data(jg_to_page=int(message.text))
                count_jg_presets = await select_count_jg_presets(message.from_user.id)
                if count_jg_presets < 5:
                    await message.answer(
                        '<b>🗂  Сохранить фильтры в пресет?</b>\n'
                        '<i>— Вы сможете подключать фильтры одним нажатием</i>',
                        reply_markup=jg_presets_kb
                    )
                    await JGParser.preset.set()
                else:
                    await message.answer(
                        '<b>❓ Запустить парсер?</b>',
                        reply_markup=start_jg_parser_kb
                    )
                    await JGParser.start_jg.set()

        else:
            await message.answer(
                f'<b>❗️ Страница должна быть больше {data["jg_from_page"]}!</b>'
            )
    except ValueError:
        await message.answer('<i><b>❗️ Введите данные в правильном формате!</b></i>')


@dp.callback_query_handler(Text(equals='add_jg_preset'), state=JGParser.preset)
@dp.throttled(anti_flood, rate=2)
async def jg_preset(call: types.CallbackQuery):
    await call.message.edit_text(
        '<b>💡 Введите название для пресета:</b>',
        reply_markup=cancel_kb
    )
    await JGParser.name.set()


@dp.message_handler(state=JGParser.name)
@dp.throttled(anti_flood, rate=2)
async def jg_preset_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_jg_preset(
        user_id=message.from_user.id,
        preset_name=message.text,
        category=data['jg_category'],
        url=data['jg_url'],
        search_text=data['jg_search_text'],
        parse_date=data['jg_parse_date'],
        parse_date_str=data['jg_parse_date_str'],
        count_reviews=data['jg_rating_count'],
        from_price=data['jg_from_price'],
        to_price=data['jg_to_price'],
        from_page=data['jg_from_page'],
        to_page=data['jg_to_page']
    )
    await message.answer(
        '<b>✅ Пресет установлен!</b>\n'
        '<b>❓ Запустить парсер?</b>',
        reply_markup=start_jg_parser_kb
    )
    await JGParser.start_jg.set()


@dp.callback_query_handler(Text(equals='start_jofogas'), state=JGParser.start_jg)
@dp.callback_query_handler(Text(equals='start_jg_without_presets'), state=JGParser.preset)
@dp.throttled(anti_flood, rate=2)
async def start_jg(call: types.CallbackQuery, state: FSMContext):
    await parse_jofogas(call, state)
