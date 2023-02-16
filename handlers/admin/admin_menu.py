from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from keyboards import admin_kb
from loader import dp


@dp.callback_query_handler(Text(equals='admin'), state='*')
async def admin(call: types.CallbackQuery):
    await call.message.edit_caption(
        caption='<b>😎 Админ меню</b>\n'
                '<i>👇 Выберите действие:</i>',
        reply_markup=admin_kb
    )


@dp.callback_query_handler(Text(equals='back_to_admin_menu'), state='*')
async def back_to_admin(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_caption(
        caption='<b>💎 Админ меню</b>\n'
                '<i>👇 Выберите действие:</i>',
        reply_markup=admin_kb
    )
    await state.reset_state(with_data=False)
