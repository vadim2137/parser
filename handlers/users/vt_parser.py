import random
import time
from datetime import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove

from keyboards import domains_kb, domains, cancel_kb, count_posts_kb, category_kb, prices_kb, subs_kb, count_reviews_kb
from keyboards.inline.presets_kb import start_vt_parser_kb, vt_presets_kb, vt_presets_list, \
    use_vt_presets_kb, use_one_vt_preset_kb, quit_vt_date, start_vt_without_preset, start_vt_preset_kb, \
    enable_registration_kb
from keyboards.reply.dates_kb import dates_kb
from loader import dp
from states import Parser
from utils import anti_flood
from utils.db_commands import select_log_filter, add_vt_preset, select_count_vt_presets, select_vt_preset_by_id, \
    delete_vt_preset, update_vt_preset_date, select_all_subs, update_vt_preset_registration
from utils.start_parse_vt import start_parse_vinted


@dp.callback_query_handler(Text(equals='vinted'), state='*')
@dp.throttled(anti_flood, rate=2)
async def vinted(call: types.CallbackQuery, state: FSMContext):
    subs = [sub.service for sub in await select_all_subs(call.from_user.id)]
    if '🌎 VINTED' in subs:
        await state.update_data(vt_work=False, wl_work=False, jg_work=False)
        count_vt_presets = await select_count_vt_presets(call.from_user.id)

        if count_vt_presets > 0:
            await call.message.edit_caption(
                '<b>🔎 Вы выбрали VINTED 🌍</b>\n\n'
                '<b>▶ Фильтры площадки:</b>\n'
                '— Дата создания объявления\n'
                '— Кол-во объявлений продавца\n'
                '— Кол-во отзывов продавца\n\n'
                '<b>🗂 Использовать пресеты?</b>',
                reply_markup=use_vt_presets_kb
            )
            await Parser.use_presets.set()
        else:
            await call.message.edit_caption(
                '<b>🔎 Вы выбрали VINTED 🌍</b>\n\n'
                '<b>▶ Фильтры площадки:</b>\n'
                '— Дата создания объявления\n'
                '— Кол-во объявлений продавца\n'
                '— Кол-во отзывов продавца\n\n'
                '<b>👇 Выберите домен из списка:</b>',
                reply_markup=domains_kb()
            )
            await Parser.domain.set()
    else:
        await call.message.edit_caption(
            '<b>❗️ Отсутствует подписка на VINTED 🌍</b>\n'
            '<b>⭐️ Тарифы на подписку:</b>',
            reply_markup=subs_kb('🌎 VINTED')
        )


@dp.callback_query_handler(Text(startswith='choose_vt_preset'), state=Parser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def choose_vt_preset(call: types.CallbackQuery):
    if call.data.split('|')[1] == 'yes':
        await call.message.edit_caption(
            '<b>🗂 Выберите пресет из списка:</b>',
            reply_markup=await vt_presets_list(call.from_user.id)
        )
    else:
        await call.message.edit_caption(
            '<b>🔎 Вы выбрали VINTED 🌍</b>\n\n'
            '<b>▶ Фильтры площадки:</b>\n'
            '— Дата создания объявления\n'
            '— Кол-во объявлений продавца\n'
            '— Кол-во отзывов продавца\n\n'
            '<b>👇 Выберите домен из списка:</b>',
            reply_markup=domains_kb()
        )
        await Parser.domain.set()


async def vt_preset(message: types.Message, preset_id: int, change_date: bool):
    vt_preset = await select_vt_preset_by_id(preset_id)

    domain = f'.{vt_preset.domain} → .{vt_preset.auto_change_domain.lower()}' \
        if vt_preset.auto_change_domain != 'False' else f'.{vt_preset.domain} → Не меняется'

    await message.edit_caption(
        f'<b>🗂 Пресет: <code>{vt_preset.preset_name}</code></b>\n\n'
        f'<b>Фильтры:</b>\n'
        f'📅 Дата публикации: <b>{vt_preset.parse_date_str}</b>\n'
        f'📅 Дата регистрации продавца: <b>{vt_preset.parse_registration_str}</b>\n'
        f'✍️ Кол-во объявлений: <b>{vt_preset.count_posts}</b>\n'
        f'⭐ Кол-во отзывов: <b>{vt_preset.count_reviews}</b>\n'
        f'👁 Домен: <b>{domain}</b>\n\n'
        f'⌨️ Ссылка: {vt_preset.url}\n\n'
        f'<b>❓ Использовать пресет?</b>',
        reply_markup=use_one_vt_preset_kb(vt_preset.id, change_date)
    )


@dp.callback_query_handler(Text(startswith='start_vt_preset'), state=Parser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def start_vt_preset(call: types.CallbackQuery):
    preset_id = int(call.data.split('|')[1])
    await vt_preset(call.message, preset_id, True)


@dp.callback_query_handler(
    Text(startswith='quit_vt_date'), state=[Parser.preset_publication, Parser.preset_registration]
)
@dp.throttled(anti_flood, rate=2)
async def quit_date_vt(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await vt_preset(data['preset_msg'], data['preset_id'], True)

    await call.message.delete()
    await Parser.use_presets.set()


@dp.callback_query_handler(Text(startswith='set_vt_date'), state=Parser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def enter_date_vt_preset(call: types.CallbackQuery, state: FSMContext):
    preset_id = int(call.data.split('|')[1])
    msg = await call.message.reply(
        '<i><b>📅 Введите минимальную</b> дату публикации <b>товара на сайте</b></i>\n'
        '<i>Пример: 2022-09-22</i>',
        reply_markup=quit_vt_date
    )

    await vt_preset(call.message, preset_id, False)
    await state.update_data(
        preset_id=preset_id,
        preset_msg=call.message,
        date_msg=msg
    )
    await Parser.preset_publication.set()


@dp.message_handler(state=Parser.preset_publication)
@dp.throttled(anti_flood, rate=2)
async def set_publication_vt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    try:
        date = message.text.split('-')
        dt = time.mktime(datetime(int(date[0]), int(date[1]), int(date[2])).timetuple())

        await update_vt_preset_date(message.from_user.id, data['preset_id'], dt, message.text)
        await vt_preset(data['preset_msg'], data['preset_id'], False)

        await data['date_msg'].edit_text(
            '<i><b>📅 Введите минимальную</b> дату регистрации <b>продавца на сайте</b></i>\n'
            '<i>Пример: 2022-09-22</i>',
            reply_markup=quit_vt_date
        )
        await Parser.preset_registration.set()
    except (ValueError, IndexError):
        await data['date_msg'].edit_text(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>\n\n'
            '<i><b>📅 Введите минимальную</b> дату публикации <b>товара на сайте</b></i>\n'
            '<i>Пример: 2022-09-22</i>',
            reply_markup=quit_vt_date
        )


@dp.message_handler(state=Parser.preset_registration)
@dp.throttled(anti_flood, rate=2)
async def set_registration_vt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.delete()
    try:
        date = message.text.split('-')
        dt = datetime(int(date[0]), int(date[1]), int(date[2]))

        await update_vt_preset_registration(message.from_user.id, data['preset_id'], dt, message.text)
        await vt_preset(data['preset_msg'], data['preset_id'], True)

        await data['date_msg'].delete()
        await Parser.use_presets.set()
    except (ValueError, IndexError):
        await data['date_msg'].edit_text(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>\n\n'
            '<i><b>📅 Введите минимальную</b> дату регистрации <b>продавца на сайте</b></i>\n'
            '<i>Пример: 2022-09-22</i>',
            reply_markup=quit_vt_date
        )


@dp.callback_query_handler(Text(startswith='pre_vt_preset'), state=Parser.use_presets)
async def pre_vt_preset(call: types.CallbackQuery):
    await call.message.edit_caption(
        '<b>❗️ Включение данного режима парсинга может значительно замедлить процесс, вы уверены, что хотите '
        'продолжить?</b>', reply_markup=start_vt_preset_kb(call.data.split('|')[1])
    )


@dp.callback_query_handler(Text(startswith='use_vt_preset'), state=Parser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def use_one_vt_preset(call: types.CallbackQuery, state: FSMContext):
    subs = [sub.service for sub in await select_all_subs(call.from_user.id)]
    if '🌎 VINTED' in subs:
        is_standard = call.data.split('|')[2] == 'standard'
        vt_preset = await select_vt_preset_by_id(int(call.data.split('|')[1]))
        await state.update_data(
            domain=vt_preset.domain,
            vt_country_code=
            [country_code[2] for country_code in domains if country_code[0] == vt_preset.domain.upper()][0],
            url=vt_preset.url,
            search_text=vt_preset.search_text,
            parse_date=vt_preset.parse_date,
            parse_date_str=vt_preset.parse_date_str,
            user_count_posts=vt_preset.count_posts,
            user_count_reviews=vt_preset.count_reviews,
            from_price=vt_preset.from_price,
            to_price=vt_preset.to_price,
            parse_registration=vt_preset.parse_registration,
            parse_registration_str=vt_preset.parse_registration_str,
            from_page=vt_preset.from_page,
            to_page=vt_preset.to_page,
            auto_change_domain=vt_preset.auto_change_domain
        )
        await start_parse_vinted(call, state, is_standard)
    else:
        await call.message.edit_caption(
            '<b>❗️ Отсутствует подписка на VINTED 🌍</b>\n'
            '<b>⭐️ Тарифы на подписку:</b>',
            reply_markup=subs_kb('🌎 VINTED')
        )


@dp.callback_query_handler(Text(startswith='del_vt_preset'), state=Parser.use_presets)
@dp.throttled(anti_flood, rate=2)
async def del_one_vt_preset(call: types.CallbackQuery):
    await delete_vt_preset(int(call.data.split('|')[1]))
    await call.answer(
        '❌ Пресет удалён!'
    )
    count_vt_presets = await select_count_vt_presets(call.from_user.id)

    if count_vt_presets > 0:
        await call.message.edit_caption(
            '🔎 Вы выбрали <b>🌍 VINTED</b>\n'
            '<b>🗂 Выберите пресет из списка:</b>',
            reply_markup=await vt_presets_list(call.from_user.id)
        )
    else:
        await call.message.edit_caption(
            '🔎 Вы выбрали <b>🌍 VINTED</b>\n'
            '<b>👇 Выберите домен из списка:</b>',
            reply_markup=domains_kb()
        )
        await Parser.domain.set()


@dp.callback_query_handler(Text(startswith='domain'), state=Parser.domain)
@dp.throttled(anti_flood, rate=2)
async def choose_domain(call: types.CallbackQuery, state: FSMContext):
    domain = call.data.split('|')[1]
    for flag in domains:
        if domain == flag[0]:
            await call.message.answer(
                f'<b>🔍 Начался поиск объявлений</b> для VINTED.{domain} {flag[1]}\n'
                f'<b>Выберите нужную категорию по которой будет производиться парсинг</b>\n'
                f'<b>Либо отправьте ссылку для поиска.</b>\n\n'
                f'<i>Пример: https://www.vinted.{domain.lower()}/vetements?catalog[]=1818</i>',
                disable_web_page_preview=True,
                reply_markup=category_kb
            )
    await state.update_data(
        domain=domain.lower(),
        vt_country_code=[country_code[2] for country_code in domains if country_code[0] == domain][0]
    )

    await Parser.category.set()


@dp.message_handler(state=Parser.category)
@dp.throttled(anti_flood, rate=2)
async def choose_category(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if f'vinted.{data["domain"]}' in message.text:
        await state.update_data(
            url=message.text,
            search_text=''
        )
    else:
        await state.update_data(
            url=f'https://www.vinted.{data["domain"]}/ubrania?search_text={message.text}&order=newest_first',
            search_text=message.text
        )

    filter = await select_log_filter(message.from_user.id)
    if not filter.post_date:
        date = str(datetime.today().date()).split('-')
        dt = datetime(int(date[0]), int(date[1]), int(date[2]))
        await state.update_data(
            parse_date=time.mktime(dt.timetuple()),
            parse_date_str=str(datetime.today().date())
        )
        if not filter.count_posts:
            await state.update_data(user_count_posts=random.randint(10, 30))
            await message.answer('🔍', reply_markup=count_reviews_kb())
            await message.answer(
                '<i><b>⭐️ Введите максимально допустимое</b> количество отзывов <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await Parser.count_reviews.set()
        else:
            await message.answer('🔍', reply_markup=count_posts_kb())
            await message.answer(
                '<i><b>📦 Введите максимально допустимое</b> количество активных объявлений <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await Parser.count_posts.set()

    else:
        await message.answer('🔍', reply_markup=dates_kb())
        await message.answer(
            '<i><b>📅 Введите минимальную</b> дату публикации <b>товара на сайте</b></i>\n'
            '<i>Пример: 2022-09-22</i>',
            reply_markup=cancel_kb
        )

        await Parser.date.set()


@dp.callback_query_handler(text_startswith='link_category', state=Parser.category)
@dp.throttled(anti_flood, rate=2)
async def choose_category_by_btn(call: types.CallbackQuery, state: FSMContext):
    category = call.data.split('|')[1]
    data = await state.get_data()
    await state.update_data(
        url=f'https://www.vinted.{data["domain"]}/vetements?{category}',
        search_text=''
    )

    filter = await select_log_filter(call.from_user.id)
    if not filter.post_date:
        date = str(datetime.today().date()).split('-')
        dt = datetime(int(date[0]), int(date[1]), int(date[2]))
        await state.update_data(
            parse_date=time.mktime(dt.timetuple()),
            parse_date_str=str(datetime.today().date())
        )
        if not filter.count_posts:
            await state.update_data(user_count_posts=random.randint(10, 30))
            await call.message.answer('🔍', reply_markup=count_reviews_kb())
            await call.message.answer(
                '<i><b>🔍 Введите максимально допустимое</b> количество отзывов <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await Parser.count_reviews.set()
        else:
            await call.message.answer('🔍', reply_markup=count_posts_kb())
            await call.message.answer(
                '<i><b>📦 Введите максимально допустимое</b> количество активных объявлений <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await Parser.count_posts.set()

    else:
        await call.message.answer('🔍', reply_markup=dates_kb())
        await call.message.answer(
            '<i><b>📅 Введите минимальную</b> дату публикации <b>товара на сайте</b></i>\n'
            '<i>Пример: 2022-09-22</i>',
            reply_markup=cancel_kb
        )

        await Parser.date.set()


@dp.message_handler(state=Parser.date)
@dp.throttled(anti_flood, rate=2)
async def get_count_posts(message: types.Message, state: FSMContext):
    try:
        date = message.text.split('-')
        dt = datetime(int(date[0]), int(date[1]), int(date[2]))
        await state.update_data(
            parse_date=time.mktime(dt.timetuple()),
            parse_date_str=message.text
        )

        filter = await select_log_filter(message.from_user.id)
        if not filter.count_posts:
            await state.update_data(user_count_posts=random.randint(10, 30))
            await message.answer('🔍', reply_markup=count_reviews_kb())
            await message.answer(
                '<i><b>⭐️ Введите максимально допустимое</b> количество отзывов <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await Parser.count_reviews.set()
        else:
            await message.answer('🔍', reply_markup=count_posts_kb())
            await message.answer(
                '<i><b>📦 Введите максимально допустимое</b> количество активных объявлений <b>у продавца</b></i>\n'
                '<i>Пример: 5</i>',
                reply_markup=cancel_kb
            )

            await Parser.count_posts.set()

    except (ValueError, IndexError):
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=Parser.count_posts)
@dp.throttled(anti_flood, rate=2)
async def get_price(message: types.Message, state: FSMContext):
    try:
        await state.update_data(user_count_posts=int(message.text))
        await message.answer('🔍', reply_markup=count_reviews_kb())
        await message.answer(
            '<i><b>⭐️ Введите максимально допустимое</b> количество отзывов <b>у продавца</b></i>\n'
            '<i>Пример: 5</i>',
            reply_markup=cancel_kb
        )

        await Parser.count_reviews.set()
    except ValueError:
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=Parser.count_reviews)
@dp.throttled(anti_flood, rate=2)
async def get_count_reviews(message: types.Message, state: FSMContext):
    try:
        await state.update_data(user_count_reviews=int(message.text))
        await message.answer('🔍', reply_markup=prices_kb)
        await message.answer(
            '<b>💵 Введите диапазон стоимости товара</b>\n'
            '<i>Пример: 1-1000</i>',
            reply_markup=cancel_kb
        )

        await Parser.price.set()
    except ValueError:
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=Parser.price)
@dp.throttled(anti_flood, rate=2)
async def get_count_reviews(message: types.Message, state: FSMContext):
    try:
        await state.update_data(
            from_price=int(message.text.split('-')[0]),
            to_price=int(message.text.split('-')[1])
        )
        await message.answer('🔍', reply_markup=ReplyKeyboardRemove())
        await message.answer(
            '<b>📅 Хотите использовать фильтр по дате регистрации?</b>\n\n'
            '<i>❗️ Включение данного фильтра может существенного замедлить процесс поиска</i>',
            reply_markup=enable_registration_kb
        )
        await Parser.use_registration.set()
    except (IndexError, ValueError):
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.callback_query_handler(Text(startswith='enable_registration'), state=Parser.use_registration)
async def enable_registration(call: types.CallbackQuery, state: FSMContext):
    enable = call.data.split('|')[1] == 'yes'
    if enable:
        await call.message.answer('🔍', reply_markup=dates_kb())
        await call.message.answer(
            '<i><b>📅 Введите минимальную</b> дату регистрации <b>продавца на сайте</b></i>\n'
            '<i>Пример: 2022-09-22</i>',
            reply_markup=cancel_kb
        )
        await Parser.registration.set()
    else:
        await call.message.delete()
        await state.update_data(
            parse_registration=datetime(1, 1, 1),
            parse_registration_str='Фильтр выключен'
        )
        await call.message.answer(
            '<b>🔍 Выберите домен, на который будет происходить автосмена</b>\n'
            '<i>Пример: с домена vinted.pl будет произведена автосмена на vinted.fr</i>',
            reply_markup=domains_kb(is_auto_change=True)
        )
        await Parser.auto_change_domain.set()


@dp.message_handler(state=Parser.registration)
@dp.throttled(anti_flood, rate=2)
async def registration(message: types.Message, state: FSMContext):
    try:
        date = message.text.split('-')
        await state.update_data(
            parse_registration=datetime(int(date[0]), int(date[1]), int(date[2])),
            parse_registration_str=message.text
        )

        await message.answer('🔍', reply_markup=ReplyKeyboardRemove())
        await message.answer(
            '<b>🔍 Выберите домен, на который будет происходить автосмена</b>\n'
            '<i>Пример: с домена vinted.pl будет произведена автосмена на vinted.fr</i>',
            reply_markup=domains_kb(is_auto_change=True)
        )

        await Parser.auto_change_domain.set()
    except (IndexError, ValueError):
        await message.answer(
            '<i><b>❗️ Введите данные в правильном формате!</b></i>'
        )


@dp.message_handler(state=Parser.from_page)
@dp.throttled(anti_flood, rate=2)
async def get_to_page(message: types.Message, state: FSMContext):
    try:
        await state.update_data(from_page=int(message.text))
        await message.answer(
            '<b>🔍 По какую страницу парсить?</b>\n'
            '<i>Пример: 20 [MAX: 20]</i>',
            reply_markup=cancel_kb
        )

        await Parser.to_page.set()
    except ValueError:
        await message.answer('<i><b>❗️ Введите данные в правильном формате!</b></i>')


@dp.message_handler(state=Parser.to_page)
@dp.throttled(anti_flood, rate=2)
async def get_auto_change_domain(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        if int(message.text) > data['from_page']:
            if int(message.text) - data['from_page'] + 1 > 20:
                await message.answer(
                    '<b>❗️ Должно быть максимум 20 страниц для парсинга!</b>'
                )
            else:
                await state.update_data(to_page=int(message.text))
                await message.answer(
                    '<b>🔍 Выберите домен, на который будет происходить автосмена</b>\n'
                    '<i>Пример: с домена vinted.pl будет произведена автосмена на vinted.fr</i>',
                    reply_markup=domains_kb(is_auto_change=True)
                )

                await Parser.auto_change_domain.set()
        else:
            await message.answer(
                f'<b>❗️ Страница должна быть больше {data["from_page"]}!</b>'
            )
    except ValueError:
        await message.answer('<i><b>❗️ Введите данные в правильном формате!</b></i>')


@dp.callback_query_handler(Text(startswith='auto_domain'), state=Parser.auto_change_domain)
@dp.throttled(anti_flood, rate=2)
async def choose_domain(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(auto_change_domain=call.data.split('|')[1])
    count_vt_presets = await select_count_vt_presets(call.from_user.id)
    if count_vt_presets < 5:
        await call.message.answer(
            '<b>🗂  Сохранить фильтры в пресет?</b>\n'
            '<i>— Вы сможете подключать фильтры одним нажатием</i>',
            reply_markup=vt_presets_kb
        )
        await Parser.preset.set()
    else:
        await call.message.answer(
            '<b>❓ Запустить парсер?</b>',
            reply_markup=start_vt_parser_kb
        )
        await Parser.start_vt.set()


@dp.callback_query_handler(Text(equals='add_vt_preset'), state=Parser.preset)
@dp.throttled(anti_flood, rate=2)
async def enter_vt_preset_name(call: types.CallbackQuery):
    await call.message.edit_text(
        '<b>💡 Введите название для пресета:</b>',
        reply_markup=cancel_kb
    )
    await Parser.name.set()


@dp.message_handler(state=Parser.name)
@dp.throttled(anti_flood, rate=2)
async def vt_preset_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_vt_preset(
        user_id=message.from_user.id,
        preset_name=message.text,
        domain=data['domain'],
        url=data['url'],
        search_text=data['search_text'],
        parse_date=data['parse_date'],
        parse_date_str=data['parse_date_str'],
        count_posts=data['user_count_posts'],
        count_reviews=data['user_count_reviews'],
        from_price=data['from_price'],
        to_price=data['to_price'],
        parse_registration=data['parse_registration'],
        parse_registration_str=data['parse_registration_str'],
        from_page=1,
        to_page=20,
        auto_change_domain=data['auto_change_domain']
    )
    await message.answer(
        '<b>✅ Пресет установлен!</b>\n'
        '<b>❓ Запустить парсер?</b>',
        reply_markup=start_vt_parser_kb
    )
    await Parser.start_vt.set()


@dp.callback_query_handler(Text(equals='start_vt_without_presets'), state=Parser.preset)
@dp.throttled(anti_flood, rate=2)
async def confirm_start(call: types.CallbackQuery):
    await call.message.edit_text(
        '<b>❓ Запустить парсер?</b>',
        reply_markup=start_vt_parser_kb
    )
    await Parser.start_vt.set()


@dp.callback_query_handler(Text(startswith='pre_start_vinted'), state=Parser.start_vt)
async def pre_start_vinted(call: types.CallbackQuery):
    await call.message.edit_text(
        '<b>❗️ Включение данного режима парсинга может значительно замедлить процесс, вы уверены, что хотите '
        'продолжить?</b>', reply_markup=start_vt_without_preset
    )


@dp.callback_query_handler(Text(startswith='start_vinted'), state=Parser.start_vt)
@dp.throttled(anti_flood, rate=2)
async def start_vt_without_presets(call: types.CallbackQuery, state: FSMContext):
    is_standard = call.data.split('|')[1] == 'standard'
    await start_parse_vinted(call, state, is_standard)
