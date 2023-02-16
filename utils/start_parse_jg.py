import asyncio
import random
import time
from datetime import datetime

import aiohttp
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.markdown import hlink
from bs4 import BeautifulSoup

from data.config import photo_1
from keyboards import stop_parser_kb
from utils.db_commands import select_viewed_post, select_log_filter, add_viewed_post, select_count_views, \
    add_last_search, add_jg_last_search
from utils.other import select_proxies


async def get_phone(item_id: str, proxy: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://apiv2.jofogas.hu/v2/items/getPhone?list_id={item_id}',
                headers={'api_key': 'jofogas-web-eFRv9myucHjnXFbj'},
                proxy=f'http://{proxy}',
                ssl=True
        ) as response:
            try:
                return (await response.json())['phone']
            except KeyError:
                return None


async def get_rating_count(seller_id: str, proxy: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://profile-api.trust-pro.mpi-internal.com/profile/sdrn:jofogas:user:{seller_id}',
                proxy=f'http://{proxy}',
                ssl=True
        ) as response:
            try:
                return (await response.json())['reputation']['feedback']['receivedCount']
            except (KeyError, TypeError):
                return 0


async def get_full_item(item_url: str, proxy: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(item_url, proxy=f'http://{proxy}', ssl=True) as response:
            soup = BeautifulSoup(await response.text(), 'lxml')
            script = soup.find_all('script')
            try:
                seller_id = script[29].text.split("account_list_id: '")[1].split("',")[0]
                rating_count = int(
                    await get_rating_count(
                        script[29].text.split("account_id: '")[1].split("',")[0],
                        proxy
                    )
                )
                seller_url = f'https://www.jofogas.hu/magyarorszag?account_list_id={seller_id}'
            except IndexError:
                seller_id = 0
                rating_count = 0
                seller_url = 'https://www.jofogas.hu/magyarorszag?account_list_id=None'

            return {
                'seller_name': script[28].text.split("'name': '")[1].split("',")[0],
                'seller_id': seller_id,
                'seller_url': seller_url,
                'date': script[22].text.split('date : "')[1].split('",')[0],
                'rating_count': rating_count
            }


async def parse_items(page: int, call: CallbackQuery, state: FSMContext, filter):
    try:
        proxies = [proxy.replace('\n', '') for proxy in await select_proxies('jofogas')]
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'https://www.jofogas.hu/magyarorszag/{(await state.get_data())["jg_category"]}?max_price={(await state.get_data())["jg_to_price"]}&min_price={(await state.get_data())["jg_from_price"]}&o={page}',
                    proxy=f'http://{random.choice(proxies)}',
                    ssl=True
            ) as response:
                soup = BeautifulSoup(await response.text(), 'lxml')
                items = soup.find_all('div', class_='contentArea')

                for item_ in items:
                    if (await state.get_data())['jg_gave'] == filter.posts_filter or not (await state.get_data())['jg_work']:
                        await state.update_data(jg_work=False)
                        return

                    await state.update_data(jg_checked=(await state.get_data())['jg_checked'] + 1)

                    item = item_.find('div', 'addToFav save-item').find('div')
                    phone = await get_phone(item.get('data-list-id'), random.choice(proxies))
                    post = await select_viewed_post(call.from_user.id, item.get('data-list-id'))
                    full_item = await get_full_item(item.get("data-url"), random.choice(proxies))
                    parse_date = full_item["date"].split('-')
                    dt = datetime(int(parse_date[0]), int(parse_date[1]), int(parse_date[2].split(' ')[0]))

                    if not phone:
                        await state.update_data(jg_no_phone=(await state.get_data())['jg_no_phone'] + 1)

                    if post:
                        await state.update_data(jg_is_viewed=(await state.get_data())["jg_is_viewed"] + 1)

                    if full_item['seller_id'] in (await state.get_data())['jg_checked_sellers']:
                        await state.update_data(
                            jg_posts_from_one_seller=(await state.get_data())["jg_posts_from_one_seller"] + 1
                        )

                    if time.mktime(dt.timetuple()) < (await state.get_data())['jg_parse_date']:
                        await state.update_data(jg_old_date=(await state.get_data())["jg_old_date"] + 1)

                    if full_item['rating_count'] > (await state.get_data())['jg_rating_count']:
                        await state.update_data(jg_many_reviews=(await state.get_data())["jg_many_reviews"] + 1)

                    if full_item['seller_id'] not in (await state.get_data())['jg_checked_sellers'] \
                            and full_item['rating_count'] <= (await state.get_data())['jg_rating_count'] \
                            and time.mktime(dt.timetuple()) >= (await state.get_data())['jg_parse_date'] \
                            and phone \
                            and not post:
                        checked_sellers = (await state.get_data())['jg_checked_sellers']
                        checked_sellers.append(full_item['seller_id'])
                        await state.update_data(jg_checked_sellers=checked_sellers)

                        count_views = await select_count_views(item.get('data-list-id'))
                        caption = [
                            f'🏷 Название: <code>{item.get("data-subject")}</code>\n' if filter.title else '',
                            f'💵 Цена: <code>{item.get("data-item-price")} FT</code>\n' if filter.price else '',
                            f'⭐️ Кол-во отзывов: <code>{full_item["rating_count"]}</code>\n',
                            f'🌎 Местоположение: <code>{item.get("data-region")}</code>\n' if filter.location else '',
                            f'🧑‍💼 Продавец: {hlink(full_item["seller_name"], full_item["seller_url"])}\n\n' if filter.name else '',
                            f'{hlink("🔺 Ссылка на объявление", item.get("data-url"))}\n',
                            f'{hlink("🔺 Ссылка на фото", item.get("data-main-photo-url"))}\n\n',
                            f'📅 Дата публикации: <b>{full_item["date"]}</b>\n\n',
                            f'☎️ Телефон: <code>{phone}</code>\n\n',
                            f'<b>{hlink("📲 Перейти в Viber", f"https://viber.click/{phone}")}</b>\n',
                            f'<b>{hlink("📫 Перейти в WhatsApp", f"https://web.whatsapp.com/send?phone={phone}")}</b>\n\n',
                            f'🪬 Видело наших пользователей: <b>{count_views}</b>'
                        ]

                        if filter.viewed_posts:
                            if count_views > 0:
                                await state.update_data(jg_have_views=(await state.get_data())["jg_have_views"] + 1)
                            else:
                                if filter.photo:
                                    await call.message.answer_photo(
                                        photo=item.get('data-main-photo-url'),
                                        caption=''.join(caption)
                                    )
                                else:
                                    await call.message.answer(''.join(caption))

                                await state.update_data(jg_gave=(await state.get_data())["jg_gave"] + 1)
                                await add_viewed_post(call.from_user.id, item.get('data-list-id'))
                        else:
                            if filter.photo:
                                await call.message.answer_photo(
                                    photo=item.get('data-main-photo-url'),
                                    caption=''.join(caption)
                                )
                            else:
                                await call.message.answer(''.join(caption))

                            await state.update_data(jg_gave=(await state.get_data())["jg_gave"] + 1)
                            await add_viewed_post(call.from_user.id, item.get('data-list-id'))
    except Exception:
        await state.update_data(jg_other=(await state.get_data())['jg_other'] + 1)


async def parse_jofogas(call: CallbackQuery, state: FSMContext):
    await state.update_data(
        jg_work=True,
        jg_checked=0,
        jg_gave=0,
        jg_no_phone=0,
        jg_many_reviews=0,
        jg_posts_from_one_seller=0,
        jg_other=0,
        jg_have_views=0,
        jg_is_viewed=0,
        jg_old_date=0,
        jg_checked_sellers=[]
    )
    data = await state.get_data()
    await add_jg_last_search(
        user_id=call.from_user.id,
        url=data['jg_url'],
        category=data['jg_category'],
        search_text=data['jg_search_text'],
        parse_date=data['jg_parse_date'],
        parse_date_str=data['jg_parse_date_str'],
        count_reviews=data['jg_rating_count'],
        from_price=data['jg_from_price'],
        to_price=data['jg_to_price'],
        from_page=data['jg_from_page'],
        to_page=data['jg_to_page']
    )
    await add_last_search(call.from_user.id, '🇭🇺 JOFOGAS')
    filter = await select_log_filter(call.from_user.id)
    start_time = int(time.time())

    await call.message.delete()
    await call.message.answer_photo(
        photo=photo_1,
        caption=f'<b>🕵🏽 Поиск объявлений запущен!</b>\n\n'
                f'<b>Фильтры:</b>\n'
                f'📅 Дата публикации: <b>{data["jg_parse_date_str"]}</b>\n'
                f'⭐ Кол-во отзывов: <b>{data["jg_rating_count"]}</b>\n'
                f'〽️ Цена: <b>от {data["jg_from_price"]} до {data["jg_to_price"]}</b>\n\n'
                f'⌨️ Ссылка: {data["jg_url"]}',
        reply_markup=stop_parser_kb
    )

    await asyncio.gather(
        *[asyncio.create_task(parse_items(page, call, state, filter)) for page in
          range(data['jg_from_page'], data['jg_to_page'])]
    )
    await call.message.answer_photo(
        photo=photo_1,
        caption=f'<b>📈 Статистика поиска</b>\n\n'
                f'Проверено: <b>{(await state.get_data())["jg_checked"]}</b>\n'
                f'Выдано: <b>{(await state.get_data())["jg_gave"]}</b>\n'
                f'Времени затрачено: <b>{time.strftime("%Mм. %Sс.", time.gmtime(int(time.time()) - start_time))}</b>\n\n'
                f'<b>Причины отклонения объявлений:</b>\n\n'
                f'Объявление давно выставлено: <b>{(await state.get_data())["jg_old_date"]}</b>\n'
                f'Объявление просмотрено другими пользователями: <b>{(await state.get_data())["jg_have_views"]}</b>\n'
                f'Объявление без телефона: <b>{(await state.get_data())["jg_no_phone"]}</b>\n'
                f'Объявление от одного продавца: <b>{(await state.get_data())["jg_posts_from_one_seller"]}</b>\n'
                f'У продавца много отзывов: <b>{(await state.get_data())["jg_many_reviews"]}</b>\n'
                f'Повторные объявления: <b>{(await state.get_data())["jg_is_viewed"]}</b>\n'
                f'По другим причинам: <b>{(await state.get_data())["jg_other"]}</b>',
        reply_markup=ReplyKeyboardRemove()
    )
