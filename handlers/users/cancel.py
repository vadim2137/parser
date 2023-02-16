from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove

from loader import dp


@dp.callback_query_handler(Text('cancel'), state='*')
async def cancel_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer('❌', reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=False)
