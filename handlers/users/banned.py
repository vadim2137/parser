from aiogram import types

from filters import IsBannedFilter
from loader import dp


@dp.message_handler(IsBannedFilter())
async def banned_message(message: types.Message):
    await message.answer('<b>🛠 Вы заблокированы в боте.</b>')


@dp.callback_query_handler(IsBannedFilter())
async def banned_message(call: types.CallbackQuery):
    await call.message.edit_text('<b>🛠 Вы заблокированы в боте.</b>')
