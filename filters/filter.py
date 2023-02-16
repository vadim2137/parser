import typing

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from utils.db_commands import select_user


class IsBannedFilter(BoundFilter):
    key = 'is_banned'

    async def check(self, message: types.Message) -> bool:
        user = await select_user(message.from_user.id)
        if not user:
            return False
        else:
            return user.is_banned
