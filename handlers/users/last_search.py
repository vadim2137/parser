from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from keyboards import subs_kb, domains
from loader import dp
from utils import anti_flood
from utils.db_commands import select_last_search, select_vt_last_search, auto_update_vt_last_search_date, \
    auto_update_jg_last_search_date, select_jg_last_search, select_all_subs, auto_update_wl_last_search_date, \
    select_wl_last_search
from utils.start_parse_jg import parse_jofogas
from utils.start_parse_vt import start_parse_vinted
from utils.start_parse_wl import start_parse_wallapop


@dp.callback_query_handler(Text('last_search'), state='*')
@dp.throttled(anti_flood, rate=2)
async def last_search(call: types.CallbackQuery, state: FSMContext):
    search = await select_last_search(call.from_user.id)

    if search:
        if search.search_class in [sub.service for sub in await select_all_subs(call.from_user.id)]:
            await state.update_data(work=False)
            if search.search_class == '🌎 VINTED':
                await auto_update_vt_last_search_date(call.from_user.id)
                vt_preset = await select_vt_last_search(call.from_user.id)
                await state.update_data(
                    vt_work=True,
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
                await start_parse_vinted(call, state, True)
            elif search.search_class == '🇭🇺 JOFOGAS':
                await auto_update_jg_last_search_date(call.from_user.id)
                jg_preset = await select_jg_last_search(call.from_user.id)
                await state.update_data(
                    jg_work=True,
                    jg_url=jg_preset.url,
                    jg_category=jg_preset.category,
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
            elif search.search_class == '🇪🇺 WALLAPOP':
                await auto_update_wl_last_search_date(call.from_user.id)
                wl_preset = await select_wl_last_search(call.from_user.id)
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
                await start_parse_wallapop(call, state, True)
        else:
            await call.message.edit_caption(
                f'<b>❗️ Отсутствует подписка на {search.search_class}</b>\n'
                f'<b>⭐️ Тарифы на подписку:</b>',
                reply_markup=subs_kb(search.search_class)
            )
    else:
        await call.answer(
            '❗️ У вас отсутствует последний поиск!',
            show_alert=True
        )
