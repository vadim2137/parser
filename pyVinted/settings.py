class Urls:
    def __init__(self, domain):
        self.API_URL = f'https://www.vinted.{domain}/api/v2/catalog/items'
        self.API_URL_GET_USER = f'https://www.vinted.{domain}/api/v2/users'
        self.HEADERS = {
            'User-Agent': 'PostmanRuntime/7.28.4',
            'Host': f'www.vinted.{domain}',
        }
        self.VINTED_AUTH_URL = f'https://www.vinted.{domain}/auth/token_refresh'
