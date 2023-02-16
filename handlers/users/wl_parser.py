import random
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qsl

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove

from keyboards import cancel_kb, count_posts_kb, dates_kb, wl_categories_kb, count_views_kb, wallapop_kb, prices_kb, \
    subs_kb, count_reviews_kb
from keyboards.inline.presets_kb import start_wl_parser_kb, use_wl_presets_kb, wl_presets_list, wl_presets_kb, \
    use_one_wl_preset_kb, quit_wl_date, start_wl_preset_kb, start_wl_without_preset
from loader import dp
from states import WLParser
from utils import anti_flood
from utils.db_commands import select_log_filter, select_count_wl_presets, select_wl_preset_by_id, \
    add_wl_preset, delete_wl_preset, update_wl_preset_date, select_all_subs
from utils.start_parse_wl import start_parse_wallapop


@dp.callback_query_handler(Text('wallapop'), state='*')
@dp.throttled(anti_flood, rate=2)
async def wallapop(call: types.CallbackQuery):
    subs = [sub.service for sub in await select_all_subs(call.from_user.id)]
    if '🇪🇺 WALLAPOP' in subs:
        await call.message.edit_caption(
            '<b>🔎 Вы выбрали WALLAPOP 🇪🇺</b>\n\n'
            '<b>▶ Фильтры площадки:</b>\n'
            '— Дата создания объявления\n'
            '— Кол-во просмотров на объявлении\n'
            '— Кол-во объявлений продавца\n'
            '— Кол-во отзывов продавца\n'
            '— Кол-во продаж продавца\n\n'
            '<b>👇 Выберите домен из списка:</b>',
            reply_markup=wallapop_kb()
        )
        await WLParser.domain.set()
    else:
        await call.message.edit_caption(
            '<b>❗️ Отсутствует подписка на WALLAPOP 🇪🇺</b>\n'
            '<b>⭐️ Тарифы на подписку:</b>',
            reply_markup=subs_kb('🇪🇺 WALLAPOP')
        )


@dp.callback_query_handler(Text(startswith='open_wl'), state=WLParser.domain)
async def choose_wallapop(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(vt_work=False, wl_work=False, tise_work=False)
    count_wl_presets = await select_count_wl_presets(call.from_user.id)
    domain = call.data.split('_')[2].split('|')
    await state.update_data(
        wl_domain=domain[0],
        wl_flag=domain[1]
    )

    if count_wl_presets > 0:
        await call.message.edit_caption(
            f'<b>🔎 Вы выбрали {domain[0]}.WALLAPOP.COM {domain[1]}</b>\n\n'
            f'<b>▶ Фильтры площадки:</b>\n'
            f'— Дата создания объявления\n'
            f'— Кол-во просмотров на объявлении\n'
            f'— Кол-во объявлений продавца\n'
            f'— Кол-во отзывов продавца\n'
            f'— Кол-во продаж продавца\n\n'
            f'<b>🗂 Использовать пресеты?</b>',
            reply_markup=use_wl_presets_kb
        )
        await WLParser.use_presets.set()
    else:
        await call.message.edit_caption(
            f'<b>🔍 Начался поиск объявлений</b> для {domain[0]}.WALLAPOP.COM {domain[1]}\n\n'
            f'<b>Выберите нужную категорию по которой будет производиться парсинг</b>\n'
            f'<b>Либо отправьте ссылку для поиска</b>\n\n'
            f'<i>Пример: https://{domain[0].lower()}.wallapop.com/app/search?category_ids=12465</i>',
            reply_markup=wl_categories_kb
        )
        await WLParser.category.set()


@dp.callback_query_handler(Text(startswith='choose_wl_preset'), state=WLParser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def choose_wl_preset(call: types.CallbackQuery, state: FSMContext):
    if call.data.split('|')[1] == 'yes':
        await call.message.edit_caption(
            '<b>🗂 Выберите пресет из списка:</b>',
            reply_markup=await wl_presets_list(call.from_user.id)
        )
    else:
        data = await state.get_data()
        await call.message.edit_caption(
            f'<b>🔍 Начался поиск объявлений</b> для {data["wl_domain"]}.WALLAPOP.COM {data["wl_flag"]}\n\n'
            f'<b>Выберите нужную категорию по которой будет производиться парсинг</b>\n'
            f'<b>Либо отправьте ссылку для поиска</b>\n\n'
            f'<i>Пример: https://{data["wl_domain"].lower()}.wallapop.com/app/search?category_ids=12465</i>',
            reply_markup=wl_categories_kb
        )
        await WLParser.category.set()


async def wt_preset(message: types.Message, preset_id: int, change_date: bool):
    wl_preset = await select_wl_preset_by_id(preset_id)
    await message.edit_caption(
        f'<b>🗂 Пресет: <code>{wl_preset.preset_name}</code></b>\n\n'
        f'<b>Фильтры:</b>\n'
        f'📅 Дата публикации: <b>{wl_preset.parse_date_str}</b>\n'
        f'✍️ Кол-во объявлений: <b>{wl_preset.count_posts}</b>\n'
        f'⭐ Кол-во отзывов: <b>{wl_preset.count_reviews}</b>\n'
        f'🛍 Кол-во продаж: <b>{wl_preset.count_sells}</b>\n'
        f'👁 Кол-во просмотров: <b>{wl_preset.post_views}</b>\n\n'
        f'⌨️ Ссылка: {wl_preset.url}\n\n'
        f'<b>❓ Использовать пресет?</b>',
        reply_markup=use_one_wl_preset_kb(wl_preset.id, change_date)
    )


@dp.callback_query_handler(Text(startswith='start_wl_preset'), state=WLParser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def start_wl_preset(call: types.CallbackQuery):
    preset_id = int(call.data.split('|')[1])
    await wt_preset(call.message, preset_id, True)


@dp.callback_query_handler(Text(startswith='quit_wl_date'), state=WLParser.preset_publication)
@dp.throttled(anti_flood, rate=2)
async def quit_date_wl(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await wt_preset(data['preset_msg'], data['preset_id'], True)

    await call.message.delete()
    await WLParser.use_presets.set()


@dp.callback_query_handler(Text(startswith='set_wl_date'), state=WLParser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def enter_date_wl_preset(call: types.CallbackQuery, state: FSMContext):
    preset_id = int(call.data.split('|')[1])
    msg = await call.message.reply(
        '<i><b>📅 Введите минимальную</b> дату публикации <b>товара на сайте</b></i>\n'
        '<i>Пример: 2022-09-22</i>',
        reply_markup=quit_wl_date
    )

    await wt_preset(call.message, preset_id, False)
    await state.update_data(
        preset_id=preset_id,
        preset_msg=call.message,
        date_msg=msg
    )
    await WLParser.preset_publication.set()


@dp.message_handler(state=WLParser.preset_publication)
@dp.throttled(anti_flood, rate=2)
async def set_date_wl_preset(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    try:
        date = message.text.split('-')
        dt = time.mktime(datetime(int(date[0]), int(date[1]), int(date[2])).timetuple())

        await update_wl_preset_date(message.from_user.id, data['preset_id'], dt, message.text)
        await wt_preset(data['preset_msg'], data['preset_id'], True)

        await data['date_msg'].delete()
        await WLParser.use_presets.set()
    except (ValueError, IndexError):
        await data['date_msg'].edit_text(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>\n\n'
            '<i><b>📅 Введите минимальную</b> дату публикации <b>товара на сайте</b></i>\n'
            '<i>Пример: 2022-09-22</i>',
            reply_markup=quit_wl_date
        )


@dp.callback_query_handler(Text(startswith='pre_wl_preset'), state=WLParser.use_presets)
async def pre_vt_preset(call: types.CallbackQuery):
    await call.message.edit_caption(
        '<b>❗️ Включение данного режима парсинга может значительно замедлить процесс, вы уверены, что хотите '
        'продолжить?</b>', reply_markup=start_wl_preset_kb(call.data.split('|')[1])
    )


@dp.callback_query_handler(Text(startswith='use_wl_preset'), state=WLParser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def use_one_wl_preset(call: types.CallbackQuery, state: FSMContext):
    subs = [sub.service for sub in await select_all_subs(call.from_user.id)]
    if '🇪🇺 WALLAPOP' in subs:
        is_standard = call.data.split('|')[2] == 'standard'
        wl_preset = await select_wl_preset_by_id(int(call.data.split('|')[1]))
        await state.update_data(
            wl_url=wl_preset.url,
            wl_keywords=wl_preset.search_text,
            wl_category_id=wl_preset.wl_category_id,
            wl_category_all=wl_preset.wl_category_all,
            wl_parse_date=wl_preset.parse_date,
            wl_parse_date_str=wl_preset.parse_date_str,
            wl_count_posts=wl_preset.count_posts,
            wl_count_reviews=wl_preset.count_reviews,
            wl_count_sells=wl_preset.count_sells,
            wl_count_views=wl_preset.post_views,
            wl_min_sale_price=wl_preset.from_price,
            wl_max_sale_price=wl_preset.to_price,
            wl_domain=wl_preset.wl_domain
        )
        await start_parse_wallapop(call, state, is_standard)
    else:
        await call.message.edit_caption(
            '<b>❗️ Отсутствует подписка на WALLAPOP 🇪🇺</b>\n'
            '<b>⭐️ Тарифы на подписку:</b>',
            reply_markup=subs_kb('🇪🇺 WALLAPOP')
        )


@dp.callback_query_handler(Text(startswith='del_wl_preset'), state=WLParser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def del_one_wl_preset(call: types.CallbackQuery, state: FSMContext):
    await delete_wl_preset(int(call.data.split('|')[1]))
    await call.answer(
        '❌ Пресет удалён!'
    )
    count_vt_presets = await select_count_wl_presets(call.from_user.id)

    if count_vt_presets > 0:
        await call.message.edit_caption(
            '🔎 Вы выбрали <b>WALLAPOP 🇪🇺</b>\n'
            '<b>🗂 Выберите пресет из списка:</b>',
            reply_markup=await wl_presets_list(call.from_user.id)
        )
    else:
        data = await state.get_data()
        await call.message.edit_caption(
            f'<b>🔍 Начался поиск объявлений</b> для {data["wl_domain"]}.WALLAPOP.COM {data["wl_flag"]}\n\n'
            f'<b>Выберите нужную категорию по которой будет производиться парсинг</b>\n'
            f'<b>Либо отправьте ссылку для поиска</b>\n\n'
            f'<i>Пример: https://{data["wl_domain"].lower()}.wallapop.com/app/search?category_ids=12465</i>',
            reply_markup=wl_categories_kb
        )
        await WLParser.category.set()


@dp.message_handler(state=WLParser.category)
@dp.throttled(anti_flood, rate=2)
async def wl_category(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if f'{data["wl_domain"].lower()}.wallapop.com' in message.text and 'category_ids=' in message.text:
        await state.update_data(
            wl_url=message.text,
            wl_keywords='',
            wl_category_id=parse_qsl(urlparse(message.text).query)[0][1]
        )
    else:
        await state.update_data(
            wl_url=f'https://{data["wl_domain"].lower()}.wallapop.com/app/search?keywords={message.text}',
            wl_keywords=message.text,
            wl_category_id='',
            wl_category_all=True
        )

    filter = await select_log_filter(message.from_user.id)
    if not filter.post_date:
        date = str(datetime.today().date()).split('-')
        dt = datetime(int(date[0]), int(date[1]), int(date[2]))
        await state.update_data(
            wl_parse_date=time.mktime(dt.timetuple()),
            wl_parse_date_str=datetime.today().date()
        )
        if not filter.count_posts:
            await state.update_data(wl_count_posts=random.randint(10, 30))
            await message.answer('🔍', reply_markup=count_reviews_kb())
            await message.answer(
                '<i><b>⭐️ Введите максимально допустимое</b> количество отзывов <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await WLParser.count_reviews.set()
        else:
            await message.answer('🔍', reply_markup=count_posts_kb())
            await message.answer(
                '<i><b>📦 Введите максимально допустимое</b> количество активных объявлений <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await WLParser.count_posts.set()

    else:
        await message.answer('🔍', reply_markup=dates_kb())
        await message.answer(
            '<i><b>📅 Введите минимальную</b> дату публикации <b>товара на сайте</b></i>\n'
            '<i>Пример: 2022-09-22</i>',
            reply_markup=cancel_kb
        )

        await WLParser.date.set()


@dp.callback_query_handler(text_startswith='wl_category', state=WLParser.category)
@dp.throttled(anti_flood, rate=2)
async def wl_choose_category_by_btn(call: types.CallbackQuery, state: FSMContext):
    category = call.data.split('|')[1] if call.data.split('|')[1] != 'all' else ''
    data = await state.get_data()
    await state.update_data(
        wl_url=f'https://{data["wl_domain"].lower()}.wallapop.com/app/search?category_ids={category}',
        wl_keywords='',
        wl_category_id=category,
        wl_category_all=True if category == '' else False
    )

    filter = await select_log_filter(call.from_user.id)
    if not filter.post_date:
        date = str(datetime.today().date()).split('-')
        dt = datetime(int(date[0]), int(date[1]), int(date[2]))
        await state.update_data(
            wl_parse_date=time.mktime(dt.timetuple()),
            wl_parse_date_str=datetime.today().date()
        )
        if not filter.count_posts:
            await state.update_data(wl_count_posts=random.randint(10, 30))
            await call.message.answer('🔍', reply_markup=count_reviews_kb())
            await call.message.answer(
                '<i><b>⭐️ Введите максимально допустимое</b> количество отзывов <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await WLParser.count_reviews.set()
        else:
            await call.message.answer('🔍', reply_markup=count_posts_kb())
            await call.message.answer(
                '<i><b>📦 Введите максимально допустимое</b> количество активных объявлений <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await WLParser.count_posts.set()

    else:
        await call.message.answer('🔍', reply_markup=dates_kb())
        await call.message.answer(
            '<i><b>📅 Введите минимальную</b> дату публикации <b>товара на сайте</b></i>\n'
            '<i>Пример: 2022-09-22</i>',
            reply_markup=cancel_kb
        )

        await WLParser.date.set()


@dp.message_handler(state=WLParser.date)
@dp.throttled(anti_flood, rate=2)
async def wl_get_count_posts(message: types.Message, state: FSMContext):
    try:
        date = message.text.split('-')
        dt = datetime(int(date[0]), int(date[1]), int(date[2]))
        await state.update_data(
            wl_parse_date=time.mktime(dt.timetuple()),
            wl_parse_date_str=message.text
        )

        filter = await select_log_filter(message.from_user.id)
        if not filter.count_posts:
            await state.update_data(wl_count_posts=random.randint(10, 30))
            await message.answer('🔍', reply_markup=count_reviews_kb())
            await message.answer(
                '<i><b>⭐️ Введите максимально допустимое</b> количество отзывов <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await WLParser.count_reviews.set()
        else:
            await message.answer('🔍', reply_markup=count_posts_kb())
            await message.answer(
                '<i><b>📦 Введите максимально допустимое</b> количество активных объявлений <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await WLParser.count_posts.set()

    except (ValueError, IndexError):
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=WLParser.count_posts)
@dp.throttled(anti_flood, rate=2)
async def wl_get_price(message: types.Message, state: FSMContext):
    try:
        await state.update_data(wl_count_posts=int(message.text))
        await message.answer('🔍', reply_markup=count_reviews_kb())
        await message.answer(
            '<i><b>⭐️ Введите максимально допустимое</b> количество отзывов <b>у продавца</b></i>\n'
            '<i>Пример: 5</i>',
            reply_markup=cancel_kb
        )

        await WLParser.count_reviews.set()
    except ValueError:
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=WLParser.count_reviews)
@dp.throttled(anti_flood, rate=2)
async def wl_get_count_reviews(message: types.Message, state: FSMContext):
    try:
        await state.update_data(wl_count_reviews=int(message.text))
        await message.answer('🔍', reply_markup=count_posts_kb())
        await message.answer(
            '<i><b>🏷 Введите максимально допустимое</b> количество продаж <b>у продавца</b></i>\n'
            '<i>Пример: 5</i>',
            reply_markup=cancel_kb
        )

        await WLParser.count_sells.set()
    except ValueError:
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=WLParser.count_sells)
@dp.throttled(anti_flood, rate=2)
async def wl_get_count_sells(message: types.Message, state: FSMContext):
    try:
        await state.update_data(wl_count_sells=int(message.text))
        await message.answer('🔍', reply_markup=count_views_kb())
        await message.answer(
            '<i><b>👁 Введите максимально допустимое</b> количество просмотров <b>на объявлении</b></i>\n'
            '<i>Пример: 500</i>',
            reply_markup=cancel_kb
        )

        await WLParser.post_views.set()
    except ValueError:
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=WLParser.post_views)
@dp.throttled(anti_flood, rate=2)
async def wl_get_count_views(message: types.Message, state: FSMContext):
    try:
        await state.update_data(wl_count_views=int(message.text))
        await message.answer('🔍', reply_markup=prices_kb)
        await message.answer(
            '<b>💵 Введите диапазон стоимости товара</b>\n'
            '<i>Пример: 1-1000</i>',
            reply_markup=cancel_kb
        )

        await WLParser.price.set()
    except ValueError:
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=WLParser.price)
@dp.throttled(anti_flood, rate=2)
async def wl_get_from_page(message: types.Message, state: FSMContext):
    await message.answer('🔍', reply_markup=ReplyKeyboardRemove())
    try:
        await state.update_data(
            wl_min_sale_price=int(message.text.split('-')[0]),
            wl_max_sale_price=int(message.text.split('-')[1])
        )
        count_wl_presets = await select_count_wl_presets(message.from_user.id)
        if count_wl_presets < 5:
            await message.answer(
                '<b>🗂  Сохранить фильтры в пресет?</b>\n'
                '<i>— Вы сможете подключать фильтры одним нажатием</i>',
                reply_markup=wl_presets_kb
            )
            await WLParser.preset.set()
        else:
            await message.answer(
                '<b>❓ Запустить парсер?</b>',
                reply_markup=start_wl_parser_kb
            )
            await WLParser.start_wl.set()
    except (IndexError, ValueError):
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.callback_query_handler(Text(equals='add_wl_preset'), state=WLParser.preset)
@dp.throttled(anti_flood, rate=2)
async def wl_preset(call: types.CallbackQuery):
    await call.message.edit_text(
        '<b>💡 Введите название для пресета:</b>',
        reply_markup=cancel_kb
    )
    await WLParser.name.set()


@dp.message_handler(state=WLParser.name)
@dp.throttled(anti_flood, rate=2)
async def wl_preset_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_wl_preset(
        user_id=message.from_user.id,
        preset_name=message.text,
        url=data['wl_url'],
        search_text=data['wl_keywords'],
        parse_date=data['wl_parse_date'],
        parse_date_str=data['wl_parse_date_str'],
        count_posts=data['wl_count_posts'],
        count_reviews=data['wl_count_reviews'],
        count_sells=data['wl_count_sells'],
        post_views=data['wl_count_views'],
        from_price=data['wl_min_sale_price'],
        to_price=data['wl_max_sale_price'],
        wl_category_id=data['wl_category_id'],
        wl_category_all=data['wl_category_all'],
        wl_domain=data['wl_domain']
    )
    await message.answer(
        '<b>✅ Пресет установлен!</b>\n'
        '<b>❓ Запустить парсер?</b>',
        reply_markup=start_wl_parser_kb
    )
    await WLParser.start_wl.set()


@dp.callback_query_handler(Text(equals='start_wl_without_presets'), state=WLParser.preset)
@dp.throttled(anti_flood, rate=2)
async def confirm_start(call: types.CallbackQuery):
    await call.message.edit_text(
        '<b>❓ Запустить парсер?</b>',
        reply_markup=start_wl_parser_kb
    )
    await WLParser.start_wl.set()


@dp.callback_query_handler(Text(startswith='pre_start_wallapop'), state=WLParser.start_wl)
async def pre_start_vinted(call: types.CallbackQuery):
    await call.message.edit_text(
        '<b>❗️ Включение данного режима парсинга может значительно замедлить процесс, вы уверены, что хотите '
        'продолжить?</b>', reply_markup=start_wl_without_preset
    )


@dp.callback_query_handler(Text(startswith='start_wallapop'), state=WLParser.start_wl)
@dp.throttled(anti_flood, rate=2)
async def start_wl_without_presets(call: types.CallbackQuery, state: FSMContext):
    is_standard = call.data.split('|')[1] == 'standard'
    await start_parse_wallapop(call, state, is_standard)
