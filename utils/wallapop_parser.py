import aiohttp
from bs4 import BeautifulSoup

from utils.other import wl_params


async def get_user_stats(user_id: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.wallapop.com/api/v3/users/{user_id}/stats', ssl=True) as response:
            return await response.json()


def get_wl_api_url(
        keywords: str,
        category_id: int,
        min_sale_price: int,
        max_sale_price: int,
        latitude: str,
        longitude: str,
        all=False
):
    url = f'https://api.wallapop.com/api/v3/general/search?keywords={keywords}&category_ids={category_id}&latitude={latitude}&longitude={longitude}&order_by=newest&filters_source=quick_filters&min_sale_price={min_sale_price}&max_sale_price={max_sale_price}'
    if all:
        url = f'https://api.wallapop.com/api/v3/general/search?keywords={keywords}&latitude={latitude}&longitude={longitude}&order_by=newest&filters_source=quick_filters&min_sale_price={min_sale_price}&max_sale_price={max_sale_price}'
    return url


def get_wl_next_page_urls(
        min_sale_price: str,
        max_sale_price: str,
        domain: str,
        search_id: str,
        category_id: str,
        category_all: bool,
        keywords: str,
        limit: int = 50
):
    urls = list()
    items_count = 0
    category_ids = f'&category_ids={category_id}' if not category_all else ''

    for _ in range(limit):
        urls.append(
            f'https://api.wallapop.com/api/v3/general/search?min_sale_price={min_sale_price}&user_province={wl_params[domain]["user_province"]}&keywords={keywords}{category_ids}&latitude={wl_params[domain]["latitude"]}&start={items_count}&user_region={wl_params[domain]["user_region"]}&user_city={wl_params[domain]["user_city"]}&search_id={search_id}&country_code={domain}&user_postal_code={wl_params[domain]["user_postal_code"]}&items_count={items_count}&filters_source=quick_filters&max_sale_price={max_sale_price}&order_by=newest&step=0&longitude={wl_params[domain]["longitude"]}'
        )
        items_count += 40
    return urls


async def get_views(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=True) as response:
            soup = BeautifulSoup(await response.text(), 'lxml')
            return soup.find_all('div', class_='card-product-detail-user-stats-right')[1].text
