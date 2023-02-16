import asyncio
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qsl

import aiohttp
import timeago
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.markdown import hlink

from data.config import photo_1
from keyboards import stop_parser_kb
from keyboards.inline.statistics import statistics
from utils.db_commands import add_wl_last_search, add_last_search, select_log_filter, add_viewed_post, \
    select_viewed_post, select_count_views
from utils.other import wl_params, get_items, create_history, add_history
from utils.wallapop_parser import get_views, get_user_stats, get_wl_api_url, get_wl_next_page_urls


async def parse_wl(items: dict, filter, call: CallbackQuery, state: FSMContext, file_name: str):
    to_file = []
    try:
        for item in items['search_objects']:

            if (await state.get_data())['wl_sent'] == filter.posts_filter or not (await state.get_data())['wl_work']:
                await state.update_data(wl_work=False)
                return

            await state.update_data(wl_checked=(await state.get_data())["wl_checked"] + 1)
            post = await select_viewed_post(call.from_user.id, item["id"])
            user_stats = await get_user_stats(item['seller_id'])
            domain = (await state.get_data())["wl_domain"]
            post_views = await get_views(f'https://{domain.lower()}.wallapop.com/item/{item["web_slug"]}')

            count_views = await select_count_views(item['id'])
            date_publication = datetime.utcfromtimestamp(item["modification_date"] / 1000)
            publication_ago = timeago.format(date_publication, datetime.now(), 'ru')

            url_to_product = f"https://{domain.lower()}.wallapop.com/item/{item['web_slug']}"
            url_to_seller = f"https://{domain.lower()}.wallapop.com/app/user/{item['seller_id']}"
            url_to_chat = 'https://es.wallapop.com/app/chat?itemId=' + item['id']
            caption = [
                f'📑 Название товара: <code>{item["title"]}</code>\n' if filter.title else '',
                f'📖 Описание: <code>{item["description"]}</code>\n' if filter.price else '',
                f'〽️ Цена: {item["price"]} {item["currency"]}\n' if filter.location else '',
                f'🌏 Местоположение: <code>{item["location"]["country_code"]}, {item["location"]["city"]}</code>\n\n',
                f'{hlink("🔺 Ссылка на объявление", url_to_product)}\n',
                f'{hlink("🔺 Ссылка на фото", item["images"][0]["original"])}\n',
                f'{hlink("🔺 Ссылка на продавца", url_to_seller)} '
                f'{"<i>(Online)</i>" if item["user"]["online"] else "<i>(Offline)</i>"}\n' if filter.name else '',
                f'{hlink("🔺 Ссылка на чат", url_to_chat)}\n\n',
                f'Дата публикации: <b>{publication_ago}</b>\n',
                f'Кол-во объявлений: <b>{user_stats["counters"][0]["value"]}</b>\n'
                f'Кол-во отзывов: <b>{user_stats["counters"][3]["value"]}</b>\n',
                f'Кол-во продаж: <b>{user_stats["counters"][2]["value"]}</b>\n'
                f'Кол-во просмотров: <b>{post_views}</b>\n\n',
                f'👻 Видело наших пользователей: <b>{count_views}</b>'
            ]

            if item["seller_id"] in (await state.get_data())['wl_checked_sellers']:
                await state.update_data(
                    wl_posts_from_one_seller=(await state.get_data())["wl_posts_from_one_seller"] + 1)

            if user_stats["counters"][0]["value"] > (await state.get_data())['wl_count_posts']:
                await state.update_data(wl_many_posts=(await state.get_data())["wl_many_posts"] + 1)

            if user_stats["counters"][3]["value"] > (await state.get_data())['wl_count_reviews']:
                await state.update_data(wl_many_reviews=(await state.get_data())["wl_many_reviews"] + 1)

            if user_stats["counters"][2]["value"] > (await state.get_data())['wl_count_sells']:
                await state.update_data(wl_many_sells=(await state.get_data())["wl_many_sells"] + 1)

            if int(post_views) > (await state.get_data())['wl_count_views']:
                await state.update_data(wl_many_post_views=(await state.get_data())["wl_many_post_views"] + 1)

            if post:
                await state.update_data(wl_is_viewed=(await state.get_data())["wl_is_viewed"] + 1)

            if item["modification_date"] < (await state.get_data())['wl_parse_date']:
                await state.update_data(wl_old_date=(await state.get_data())["wl_old_date"] + 1)

            if item["location"]["country_code"] != domain:
                await state.update_data(wl_another_country=(await state.get_data())['wl_another_country'] + 1)

            if item["modification_date"] >= (await state.get_data())['wl_parse_date'] \
                    and 0 <= user_stats["counters"][0]["value"] <= (await state.get_data())['wl_count_posts'] \
                    and user_stats["counters"][3]["value"] <= (await state.get_data())['wl_count_reviews'] \
                    and user_stats["counters"][2]["value"] <= (await state.get_data())['wl_count_sells'] \
                    and int(post_views) <= (await state.get_data())['wl_count_views'] \
                    and not item["seller_id"] in (await state.get_data())['wl_checked_sellers'] \
                    and not post \
                    and item["location"]["country_code"] == domain:

                checked_sellers = (await state.get_data())['wl_checked_sellers']
                checked_sellers.append(item['seller_id'])
                await state.update_data(wl_checked_sellers=checked_sellers)
                if filter.viewed_posts:
                    if count_views > 0:
                        await state.update_data(wl_have_views=(await state.get_data())["wl_have_views"] + 1)
                    else:
                        to_file.append([item["title"], url_to_product, url_to_chat])
                        if filter.photo:
                            await call.message.answer_photo(
                                photo=item['images'][0]['original'],
                                caption=''.join(caption)
                            )
                        else:
                            await call.message.answer(''.join(caption))

                        await state.update_data(wl_sent=(await state.get_data())["wl_sent"] + 1)
                        await add_viewed_post(call.from_user.id, item['id'])
                else:
                    to_file.append([item["title"], url_to_product, url_to_chat])
                    if filter.photo:
                        await call.message.answer_photo(
                            photo=item['images'][0]['original'],
                            caption=''.join(caption)
                        )
                    else:
                        await call.message.answer(''.join(caption))

                    await state.update_data(wl_sent=(await state.get_data())["wl_sent"] + 1)
                    await add_viewed_post(call.from_user.id, item['id'])

    except Exception:
        await state.update_data(wl_other=(await state.get_data())["wl_other"] + 1)
    finally:
        if len(to_file):
            await add_history(file_name, to_file)


async def get_wl_urls(state: FSMContext):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                get_wl_api_url(
                    (await state.get_data())['wl_keywords'],
                    (await state.get_data())['wl_category_id'],
                    (await state.get_data())['wl_min_sale_price'],
                    (await state.get_data())['wl_max_sale_price'],
                    wl_params[(await state.get_data())['wl_domain']]['latitude'],
                    wl_params[(await state.get_data())['wl_domain']]['longitude'],
                    (await state.get_data())['wl_category_all']
                ),
                ssl=True
        ) as response:
            next_page = response.headers['X-NextPage']

            search_url = 'https://api.wallapop.com/api/v3/general/search?'
            search_url += next_page
            queries = dict(parse_qsl(urlparse(search_url).query))
            return get_wl_next_page_urls(
                queries['min_sale_price'],
                queries['max_sale_price'],
                (await state.get_data())['wl_domain'],
                queries['search_id'],
                (await state.get_data())['wl_category_id'],
                (await state.get_data())['wl_category_all'],
                (await state.get_data())['wl_keywords'],
                25
            )


async def start_parse_wallapop(call: CallbackQuery, state: FSMContext, is_standard: bool):
    await state.update_data(
        wl_work=True,
        wl_is_viewed=0,
        wl_checked=0,
        wl_sent=0,
        wl_many_posts=0,
        wl_many_reviews=0,
        wl_many_sells=0,
        wl_many_post_views=0,
        wl_old_date=0,
        wl_have_views=0,
        wl_posts_from_one_seller=0,
        wl_another_country=0,
        wl_other=0,
        wl_checked_sellers=[]
    )

    data = await state.get_data()
    await add_wl_last_search(
        user_id=call.from_user.id,
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
    await add_last_search(call.from_user.id, '🇪🇺 WALLAPOP')

    filter = await select_log_filter(call.from_user.id)
    start_time = int(time.time())
    await call.message.delete()

    file_name = await create_history()
    await call.message.answer_photo(
        photo=photo_1,
        caption=f'<b>🕵🏽 Поиск объявлений запущен!</b>\n\n'
                f'<b>Фильтры:</b>\n'
                f'🤖 Тип поиска: {"<b>Стандартный</b>" if is_standard else "<b>Фоновый</b>"}\n'
                f'📅 Дата публикации: <b>{data["wl_parse_date_str"]}</b>\n'
                f'✍️ Кол-во объявлений: <b>{data["wl_count_posts"]}</b>\n'
                f'⭐ Кол-во отзывов: <b>{data["wl_count_reviews"]}</b>\n'
                f'🛍 Кол-во продаж: <b>{data["wl_count_sells"]}</b>\n'
                f'👁 Кол-во просмотров: <b>{data["wl_count_views"]}</b>\n'
                f'〽️ Цена: <b>от {data["wl_min_sale_price"]} до {data["wl_max_sale_price"]}</b>\n\n'
                f'⌨️ Ссылка: {data["wl_url"]}',
        reply_markup=stop_parser_kb
    )

    if is_standard:
        tasks = [asyncio.create_task(get_items(url)) for url in await get_wl_urls(state)]
        results = [await task for task in tasks]

        await asyncio.gather(*[asyncio.create_task(parse_wl(items, filter, call, state, file_name)) for items in results])
    else:
        while ((await state.get_data())['wl_sent'] < 6) and ((await state.get_data())['wl_work']):
            items = await get_items((await get_wl_urls(state))[0])
            await asyncio.gather(*[asyncio.create_task(parse_wl(items, filter, call, state, file_name))])


    msg = await call.message.answer_photo(
        photo=photo_1,
        caption=f'<b>📈 Статистика поиска</b>\n\n'
                f'Проверено: <b>{(await state.get_data())["wl_checked"]}</b>\n'
                f'Выдано: <b>{(await state.get_data())["wl_sent"]}</b>\n'
                f'Времени затрачено: <b>{time.strftime("%Mм. %Sс.", time.gmtime(int(time.time()) - start_time))}</b>\n\n'
                f'<b>Причины отклонения объявлений:</b>\n\n'
                f'Объявление давно выставлено: <b>{(await state.get_data())["wl_old_date"]}</b>\n'
                f'Объявление просмотрено другими пользователями: <b>{(await state.get_data())["wl_have_views"]}</b>\n'
                f'Объявление от одного продавца: <b>{(await state.get_data())["wl_posts_from_one_seller"]}</b>\n'
                f'Объявление из другой страны: <b>{(await state.get_data())["wl_another_country"]}</b>\n'
                f'На объявлении много просмотров: <b>{(await state.get_data())["wl_many_post_views"]}</b>\n'
                f'У продавца много объявлений: <b>{(await state.get_data())["wl_many_posts"]}</b>\n'
                f'У продавца много отзывов: <b>{(await state.get_data())["wl_many_reviews"]}</b>\n'
                f'У продавца много продаж: <b>{(await state.get_data())["wl_many_sells"]}</b>\n'
                f'Повторные объявления: <b>{(await state.get_data())["wl_is_viewed"]}</b>\n'
                f'По другим причинам: <b>{(await state.get_data())["wl_other"]}</b>',
        reply_markup=ReplyKeyboardRemove()
    )
    await msg.reply('<b>📈 Хотите экспортировать ссылки на чат с продавцом?</b>', reply_markup=statistics(file_name))
    await state.reset_state(with_data=False)
