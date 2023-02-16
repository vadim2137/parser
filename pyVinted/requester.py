import aiohttp
from aiohttp import ServerDisconnectedError, ClientConnectorError

MAX_RETRIES = 5


class Requester:

    def __init__(self, headers, auth_url, proxy):
        self.session = aiohttp.ClientSession(headers=headers)
        self.VINTED_AUTH_URL = auth_url
        self.proxy = proxy

    async def get(self, url, params=None):
        """
        Perform a http get request.
        :param url: str
        :param params: dict, optional
        :return: dict
            Json format
        """
        tried = 0

        while tried < MAX_RETRIES:
            tried += 1
            try:
                response = await self.session.get(url, params=params, proxy=f'http://{self.proxy}', ssl=False)
                if response.status == 401 and tried < MAX_RETRIES:
                    await self.setCookies()

                elif response.status == 200 or tried == MAX_RETRIES:
                    return response
            except (ServerDisconnectedError, ClientConnectorError):
                pass

    async def post(self, url, params=None):
        response = await self.session.post(url, params=params, proxy=f'http://{self.proxy}', ssl=False)
        response.raise_for_status()
        return response

    async def setCookies(self):

        self.session.cookie_jar.clear()
        try:

            await self.post(self.VINTED_AUTH_URL)

        except Exception:
            pass
