import aiohttp
from bs4 import BeautifulSoup


async def get_detail_vt(item_url: str, domain: str):
    async with aiohttp.ClientSession() as session:
        print(item_url)
        async with session.get(item_url, ssl=False) as response:
            soup = BeautifulSoup(await response.text(), 'lxml')
            return {
                'chat': f'https://vinted.{domain}{soup.find("a", class_="c-button--default c-button--medium c-button c-button--truncated").get("href")}',
                'description':
                    eval(str(soup.find('script', {'data-component-name': 'ItemDescription'}).text))['content']['description']
            }
