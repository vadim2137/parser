from aiogram import types
from aiogram.dispatcher.filters import Text

from keyboards import back_to_start_kb
from loader import dp
from utils import anti_flood


@dp.callback_query_handler(Text('help'), state='*')
@dp.throttled(anti_flood, rate=1)
async def parse_settings(call: types.CallbackQuery):
    await call.message.edit_caption(
        caption='По вопросам сотрудничества - @iconic_pwnz\n'
                'По любым другим вопросам/проблемам - @AdvancedShopSupport',
        reply_markup=back_to_start_kb
    )
