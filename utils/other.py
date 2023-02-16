import datetime
import time
from uuid import uuid4

import aiofiles
import aiohttp
from aiocsv import AsyncWriter


def hours_to_seconds(hours: int):
    return hours * 3600


def hours_to_days(hours: int):
    return int(hours / 24)


async def select_proxies(service: str):
    async with aiofiles.open(f'proxy/{service}.txt') as file:
        return await file.readlines()


async def create_history():
    file_name = str(uuid4())
    async with aiofiles.open(f'history/{file_name}.csv', 'w', encoding='utf-8', newline="") as afp:
        writer = AsyncWriter(afp, dialect="unix")
        await writer.writerow(["Название товара", "Ссылка на продавца", "Ссылка на чат"])
    return file_name


async def add_history(file_name: str, to_file: list):
    async with aiofiles.open(f'history/{file_name}.csv', 'a', encoding='utf-8', newline="") as afp:
        writer = AsyncWriter(afp, dialect="unix")
        await writer.writerows(to_file)
    return file_name


async def get_items(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=True) as response:
            return await response.json()


def get_time_sub(get_time: int):
    left_time = get_time - int(time.time())
    left_time = str(datetime.timedelta(seconds=left_time))
    left_time = left_time.replace('days', 'дней').replace('day', 'день')

    return left_time


wl_params = {
    'ES': {
        'user_province': 'Madrid',
        'user_city': 'Madrid',
        'user_region': 'Comunidad+de+Madrid',
        'latitude': '40.41956',
        'longitude': '-3.69196',
        'user_postal_code': '28014'
    },
    'FR': {
        'user_province': 'Paris',
        'user_city': 'Paris',
        'user_region': 'Ile-de-France',
        'latitude': '48.85718',
        'longitude': '2.34141',
        'user_postal_code': '75001'
    },
    'PT': {
        'user_province': 'Lisboa',
        'user_city': 'Lisboa',
        'user_region': 'Lisboa',
        'latitude': '38.736946',
        'longitude': '-9.142685',
        'user_postal_code': '1000-042'
    },
    'IT': {
        'user_province': 'Roma',
        'user_city': 'Roma',
        'user_region': 'Lazio',
        'latitude': '41.8905',
        'longitude': '-9.142685',
        'user_postal_code': '12.4942'
    }
}

