from typing import Dict

from aiohttp.web_exceptions import HTTPError

from . import settings
from pyVinted.items import Items
from pyVinted.requester import Requester


class Vinted:
    """
    This class is built to connect with the pyVinted API.

    It's main goal is to be able to retrieve items from a given url search.\n

    """

    def __init__(self, domain, proxy):
        """
        Args:
            Proxy : proxy to be used to bypass vinted's limite rate

        """
        self.domain = domain
        self.proxy = proxy

        self.items = Items(
            settings.Urls(domain).API_URL,
            settings.Urls(domain).HEADERS,
            settings.Urls(domain).VINTED_AUTH_URL,
            self.proxy
        )

    async def get_user(self, user_id) -> Dict:
        try:
            response = await Requester(
                settings.Urls(self.domain).HEADERS,
                settings.Urls(self.domain).VINTED_AUTH_URL,
                self.proxy
            ).get(url=f'{settings.Urls(self.domain).API_URL_GET_USER}/{user_id}')
            print(self.proxy)
            response.raise_for_status()
            user = await response.json()
            user = user['user']

            return user

        except HTTPError as err:
            raise err
