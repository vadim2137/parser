from aiogram.dispatcher.filters import Text, ChatTypeFilter, ContentTypeFilter

from loader import dp
from aiogram import types

from utils import anti_flood


@dp.callback_query_handler(Text(equals='echo'), state='*')
@dp.throttled(anti_flood, rate=2)
async def echo_call_handler(call: types.CallbackQuery):
    await call.answer(
        '❗️ Кнопка не активна!'
    )


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), state='*')
async def echo_message_handler(message: types.Message):
    await message.answer(
        '<b>❗️ Вы ввели неверную команду!</b>\n'
        '<i>💡 Введите /start</i>'
    )
