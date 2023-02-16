from aiogram import types

from data.config import ADMINS_ID
from loader import dp


@dp.message_handler(content_types=types.ContentType.ANY, user_id=ADMINS_ID, state='*')
async def get_content(message: types.Message):
    if types.ContentType.ANIMATION == message.content_type:
        await message.answer(
            f'<code>{message.animation.file_id}</code>'
        )
    elif types.ContentType.PHOTO == message.content_type:
        await message.answer(
            f'<code>{message.photo[-1].file_id}</code>'
        )
