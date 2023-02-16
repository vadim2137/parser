import asyncio
import random
import time
import traceback
from datetime import datetime

import timeago
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.markdown import hlink

from data.config import photo_1
from keyboards import stop_parser_kb
from keyboards.inline.statistics import statistics
from utils.other import select_proxies, create_history, add_history
from pyVinted import Vinted
from utils.db_commands import add_viewed_post, select_count_views, select_viewed_post, select_log_filter, \
    add_vt_last_search, add_last_search
from utils.vinted_parser import get_detail_vt


async def parse_vt(items: list, filter, call: CallbackQuery, state: FSMContext, file_name: str):
    to_file = []
    try:
        for item in items:
            print('Start Parsing')

            if (await state.get_data())['sent'] == filter.posts_filter or not (await state.get_data())['vt_work']:
                return

            await state.update_data(checked=(await state.get_data())["checked"] + 1)
            proxies = [proxy.replace('\n', '') for proxy in await select_proxies('vinted')]
            vinted = Vinted((await state.get_data())['domain'], proxy=random.choice(proxies))

            user = await vinted.get_user(item.user_id)
            parse_date = str(item.created_at_ts.date()).split('-')
            dt = datetime(int(parse_date[0]), int(parse_date[1]), int(parse_date[2]))
            post = await select_viewed_post(call.from_user.id, str(item.id))
            all_feedback_count = user['positive_feedback_count'] + user['neutral_feedback_count'] + user[
                'negative_feedback_count']

            user_verified = user['verification']['phone']['verified_at']
            if user_verified is not None:
                user_registration = datetime.strptime(user_verified, '%Y-%m-%dT%H:%M:%S%z')
                registration_ago = timeago.format(user_registration, datetime.now(user_registration.tzinfo), 'ru')
            else:
                user_registration = datetime(2, 1, 1)
                registration_ago = 'Неизвестно'
            print('Getted User')

            if user['id'] in (await state.get_data())['vt_checked_sellers']:
                await state.update_data(posts_from_one_seller=(await state.get_data())["posts_from_one_seller"] + 1)

            if user_registration.replace(tzinfo=None) < (await state.get_data())['parse_registration']:
                await state.update_data(old_registration=(await state.get_data())["old_registration"] + 1)

            if user['item_count'] > (await state.get_data())['user_count_posts']:
                await state.update_data(many_posts=(await state.get_data())["many_posts"] + 1)

            if all_feedback_count > (await state.get_data())['user_count_reviews']:
                await state.update_data(many_reviews=(await state.get_data())["many_reviews"] + 1)

            if time.mktime(dt.timetuple()) < (await state.get_data())['parse_date']:
                await state.update_data(old_date=(await state.get_data())["old_date"] + 1)

            if post:
                await state.update_data(is_viewed=(await state.get_data())["is_viewed"] + 1)

            if user['country_code'] != (await state.get_data())['vt_country_code']:
                await state.update_data(vt_another_country=(await state.get_data())['vt_another_country'] + 1)

            if time.mktime(dt.timetuple()) >= (await state.get_data())['parse_date'] \
                    and user_registration.replace(tzinfo=None) >= (await state.get_data())['parse_registration'] \
                    and user['item_count'] <= (await state.get_data())['user_count_posts'] \
                    and all_feedback_count <= (await state.get_data())['user_count_reviews'] \
                    and user["country_code"] == (await state.get_data())['vt_country_code'] \
                    and not user['id'] in (await state.get_data())['vt_checked_sellers'] \
                    and not post:

                checked_sellers = (await state.get_data())['vt_checked_sellers']
                checked_sellers.append(user['id'])
                await state.update_data(vt_checked_sellers=checked_sellers)
                count_views = await select_count_views(str(item.id))
                item_url = item.url.replace((await state.get_data())["domain"],
                                            (await state.get_data())["auto_change_domain"].lower()) \
                    if (await state.get_data())["auto_change_domain"] != 'False' else item.url

                seller_url = item.profile_url.replace("." + (await state.get_data())["domain"],
                                                      "." + (await state.get_data())["auto_change_domain"].lower()) if \
                    (await state.get_data())["auto_change_domain"] != 'False' else item.profile_url

                detail_vt = await get_detail_vt(item_url, (await state.get_data())["auto_change_domain"].lower() if
                (await state.get_data())["auto_change_domain"] != 'False' else (await state.get_data())["domain"])

                date_publication = datetime.utcfromtimestamp(item.raw_timestamp)
                publication_ago = timeago.format(date_publication, datetime.now(), 'ru')
                caption = [
                    f'📑 Название товара: <code>{item.title}</code>\n' if filter.title else '',
                    f'📖 Описание: <code>{detail_vt["description"]}</code>\n'
                    f'〽️ Цена: <code>{item.price} {item.currency}</code>\n' if filter.price else '',
                    f'🌏 Местоположение: <code>{user["country_title"]}</code>\n\n' if filter.location else '',
                    f'{hlink("🔺 Ссылка на объявление", item_url)}\n',
                    f'{hlink("🔺 Ссылка на фото", item.photo)}\n',
                    f'{hlink("🔺 Ссылка на продавца", seller_url)}\n' if filter.name else '',
                    f'{hlink("🔺 Ссылка на чат", detail_vt["chat"])}\n\n',
                    f'Дата регистрации продавца: <b>{registration_ago}</b>\n',
                    f'Дата публикации: <b>{publication_ago}</b>\n',
                    f'Кол-во объявлений: <b>{user["item_count"]}</b>\n',
                    f'Кол-во отзывов: <b>{all_feedback_count}</b>\n\n',
                    f'👻 Видело наших пользователей: <b>{count_views}</b>'
                ]

                if filter.viewed_posts:
                    if count_views > 0:
                        await state.update_data(have_views=(await state.get_data())['have_views'] + 1)
                    else:
                        to_file.append([item.title, item_url, detail_vt["chat"]])
                        if filter.photo:
                            await call.message.answer_photo(
                                photo=item.photo,
                                caption=''.join(caption)
                            )
                        else:
                            await call.message.answer(''.join(caption))

                        await state.update_data(sent=(await state.get_data())['sent'] + 1)
                        await add_viewed_post(call.from_user.id, str(item.id))
                else:
                    to_file.append([item.title, item_url, detail_vt["chat"]])
                    if filter.photo:
                        await call.message.answer_photo(
                            photo=item.photo,
                            caption=''.join(caption)
                        )
                    else:
                        await call.message.answer(''.join(caption))

                    await state.update_data(sent=(await state.get_data())['sent'] + 1)
                    await add_viewed_post(call.from_user.id, str(item.id))
    except Exception as err:
        traceback.print_exc()
        print(err)
        await state.update_data(other=(await state.get_data())['other'] + 1)
    finally:
        if len(to_file):
            await add_history(file_name, to_file)


async def start_parse_vinted(call: CallbackQuery, state: FSMContext, is_standard: bool):
    await state.update_data(
        vt_work=True,
        is_viewed=0,
        checked=0,
        sent=0,
        many_posts=0,
        many_reviews=0,
        old_date=0,
        old_registration=0,
        have_views=0,
        posts_from_one_seller=0,
        other=0,
        vt_another_country=0,
        vt_checked_sellers=[],
        from_page=1,
        to_page=20
    )

    data = await state.get_data()

    await add_vt_last_search(
        user_id=call.from_user.id,
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
        from_page=data['from_page'],
        to_page=data['to_page'],
        auto_change_domain=data['auto_change_domain']
    )
    await add_last_search(call.from_user.id, '🌎 VINTED')

    domain = f'.{data["domain"]} → .{data["auto_change_domain"].lower()}' \
        if data['auto_change_domain'] != 'False' else f'.{data["domain"]} → Не меняется'

    filter = await select_log_filter(call.from_user.id)
    proxies = [proxy.replace('\n', '') for proxy in await select_proxies('vinted')]
    vinted = Vinted(data['domain'], proxy=random.choice(proxies))

    start_time = int(time.time())
    await call.message.delete()

    file_name = await create_history()
    await call.message.answer_photo(
        photo=photo_1,
        caption=f'<b>🕵🏽 Поиск объявлений запущен!</b>\n\n'
                f'<b>Фильтры:</b>\n'
                f'🤖 Тип поиска: {"<b>Стандартный</b>" if is_standard else "<b>Фоновый</b>"}\n'
                f'📅 Дата публикации: <b>{data["parse_date_str"]}</b>\n'
                f'📅 Дата регистрации продавца: <b>{data["parse_registration_str"]}</b>\n'
                f'✍️ Кол-во объявлений: <b>{data["user_count_posts"]}</b>\n'
                f'⭐ Кол-во отзывов: <b>{data["user_count_reviews"]}</b>\n'
                f'👁 Домен: <b>{domain}</b>\n'
                f'〽️ Цена: <b>от {data["from_price"]} до {data["to_price"]}</b>\n\n'
                f'⌨️ Ссылка: {data["url"]}',
        reply_markup=stop_parser_kb
    )

    if is_standard:
        tasks = [asyncio.create_task(
            vinted.items.search(
                url=data['url'], nbrItems=100, page=page, time=time.time(),
                search_text=data['search_text'], price_to=data['to_price'],
                price_from=data['from_price']
            )
        ) for page in range(data['from_page'], data['to_page'] + 1)]
        results = [await task for task in tasks]
        await asyncio.gather(
            *[asyncio.create_task(parse_vt(items, filter, call, state, file_name)) for items in results]
        )
    else:
        while ((await state.get_data())['sent'] < 6) and ((await state.get_data())['vt_work']):
            items = await vinted.items.search(
                url=data['url'], time=time.time(), search_text=data['search_text'],
                price_to=data['to_price'], price_from=data['from_price']
            )
            await asyncio.gather(*[asyncio.create_task(parse_vt(items, filter, call, state, file_name))])

    msg = await call.message.answer_photo(
        photo=photo_1,
        caption=f'<b>📈 Статистика поиска</b>\n\n'
                f'Проверено: <b>{(await state.get_data())["checked"]}</b>\n'
                f'Выдано: <b>{(await state.get_data())["sent"]}</b>\n'
                f'Времени затрачено: <b>{time.strftime("%Mм. %Sс.", time.gmtime(int(time.time()) - start_time))}</b>\n\n'
                f'<b>Причины отклонения объявлений:</b>\n\n'
                f'Объявление давно выставлено: <b>{(await state.get_data())["old_date"]}</b>\n'
                f'Продавец давно зарегистрирован: <b>{(await state.get_data())["old_registration"]}</b>\n'
                f'Объявление просмотрено другими пользователями: <b>{(await state.get_data())["have_views"]}</b>\n'
                f'Объявление от одного продавца: <b>{(await state.get_data())["posts_from_one_seller"]}</b>\n'
                f'Объявления из другой страны: <b>{(await state.get_data())["vt_another_country"]}</b>\n'
                f'У продавца много объявлений: <b>{(await state.get_data())["many_posts"]}</b>\n'
                f'У продавца много отзывов: <b>{(await state.get_data())["many_reviews"]}</b>\n'
                f'Повторные объявления: <b>{(await state.get_data())["is_viewed"]}</b>\n'
                f'По другим причинам: <b>{(await state.get_data())["other"]}</b>',
        reply_markup=ReplyKeyboardRemove()
    )
    await msg.reply('<b>📈 Хотите экспортировать ссылки на чат с продавцом?</b>', reply_markup=statistics(file_name))
