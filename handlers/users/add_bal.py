from aiogram import types
from aiogram.dispatcher.filters import Text

from keyboards.inline.payments_kb import payment_methods_kb
from loader import dp


@dp.callback_query_handler(Text('add_balance'), state='*')
async def add_balance(call: types.CallbackQuery):
    await call.message.edit_caption(
        '<b>💳 Выберите способ пополнения:</b>',
        reply_markup=payment_methods_kb
    )
