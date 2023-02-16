from typing import List, Dict
from urllib.parse import urlparse, parse_qsl

from aiohttp import ClientResponseError

from pyVinted.items.item import Item
from pyVinted.requester import Requester


class Items:
    def __init__(self, api_url, headers, auth_url, proxy):
        self.api_url = api_url
        self.HEADERS = headers
        self.AUTH_URL = auth_url
        self.proxy = proxy

    async def search(self, url,
                     nbrItems: int = 20,
                     page: int = 1,
                     time: int = None,
                     search_text='',
                     price_to='',
                     price_from='',
                     json: bool = False) -> List[Item]:
        """
        Retrieves items from a given search url on vited.

        Args:
            url (str): The url of the research on vinted.
            nbrItems (int): Number of items to be returned (default 20).
            page (int): Page number to be returned (default 1).

        """

        params = self.parseUrl(
            url, nbrItems, page, time,
            search_text, price_to, price_from
        )
        url = self.api_url

        try:
            #print(self.HEADERS, self.AUTH_URL, self.proxy,url,params,sep='\n')
            response = await Requester(self.HEADERS, self.AUTH_URL, self.proxy).get(url=url, params=params)
            print(url, self.HEADERS, self.AUTH_URL, self.proxy)
            response.raise_for_status()
            items = await response.json()
            items = items["items"]
            with open("debug.txt", "w") as my_file:
                my_file.write(str(items))
            if not json:
                return [Item(_item) for _item in items]
            else:
                return items

        except ClientResponseError:
            pass

    def parseUrl(self, url, nbrItems=20, page=1, time=None, search_text='', price_to='', price_from='') -> Dict:
        """
        Parse Vinted search url to get parameters the for api call.

        Args:
            url (str): The url of the research on vinted.
            nbrItems (int): Number of items to be returned (default 20).
            page (int): Page number to be returned (default 1).

        """
        querys = parse_qsl(urlparse(url).query)
        params = {
            "search_text": search_text,
            "catalog_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "catalog[]"])
            ),
            "color_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "color_id[]"])
            ),
            "brand_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "brand_id[]"])
            ),
            "size_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "size_id[]"])
            ),
            "material_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "material_id[]"])
            ),
            "status_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "status[]"])
            ),
            "country_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "country_id[]"])
            ),
            "city_ids": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "city_id[]"])
            ),
            "is_for_swap": ",".join(
                map(str, [1 for tpl in querys if tpl[0] == "disposal[]"])
            ),
            "currency": ",".join(
                map(str, [tpl[1] for tpl in querys if tpl[0] == "currency"])
            ),
            "price_to": price_to,
            "price_from": price_from,
            "page": page,
            "per_page": nbrItems,
            "order": "newest_first",
            "time": time
        }

        return params
