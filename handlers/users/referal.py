from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.utils.deep_linking import get_start_link

from keyboards import back_to_start_kb
from loader import dp
from utils.db_commands import select_count_ref_users


@dp.callback_query_handler(Text('referal'))
async def referal(call: types.CallbackQuery):
    await call.message.edit_caption(
        f'<b>🤝 Реферальная система</b>\n'
        f'Вы пригласили: <b>{(await select_count_ref_users(call.from_user.id))} человек</b>\n\n'
        f'💌 За любую покупку Вашего реферала вы получите 20% на свой баланс\n\n'
        f'🔗 Ваша реферальная ссылка:\n{(await get_start_link(call.from_user.id))}',
        reply_markup=back_to_start_kb
    )
