import time
from datetime import datetime, timezone


class Item:
    def __init__(self, data):
        self.raw_data = data
        self.id = data["id"]
        self.title = data["title"]
        self.brand_title = data["brand_title"]
        try:
            self.size_title = data["size_title"]
        except:
            self.size_title = data["size_title"]
        self.currency = data["currency"]
        self.price = data["price"]
        try:
            self.photo = data["photo"]["url"]
            self.created_at_ts = datetime.fromtimestamp(
                data["photo"]["high_resolution"]["timestamp"], tz=timezone.utc
            )
            self.raw_timestamp = data["photo"]["high_resolution"]["timestamp"]
        except Exception:
            self.photo = 'AgACAgIAAxkBAAJ4IWNJBMaDmqgV-f_ZG5dT-moUlJNgAALOvTEb185ISh5rqvMjt-s5AQADAgADbQADKgQ'
            self.created_at_ts = ''
            self.raw_timestamp = int(time.time())

        self.url = data["url"]
        self.user_id = data['user']['id']
        self.profile_url = data['user']['profile_url']

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(('id', self.id))

    # def isNewItem(self, minutes=3):
    #     delta = datetime.now(timezone.utc) - self.created_at_ts
    #     return delta.total_seconds() < minutes * 60

