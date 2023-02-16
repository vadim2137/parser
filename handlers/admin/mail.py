from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from asyncio import sleep

from keyboards import back_to_admin_kb
from loader import dp, bot
from states import Mail
from utils.db_commands import select_users


@dp.callback_query_handler(Text(equals='mail'), state='*')
async def mail(call: types.CallbackQuery):
    await call.message.edit_caption(
        '<b>💌 Отправьте сообщение для рассылки:</b>',
        reply_markup=back_to_admin_kb
    )
    await Mail.mail.set()


@dp.message_handler(state=Mail.mail, content_types=types.ContentType.ANY)
async def mail_on(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    send_user = 0
    exception_user = 0
    await message.answer(
        '<b>⏳ Запускаю рассылку...</b>'
    )
    for user in await select_users():
        try:
            await bot.copy_message(
                chat_id=user.user_id, message_id=message.message_id,
                from_chat_id=message.from_user.id
            )
            await sleep(0.33)
            send_user += 1
        except Exception:
            exception_user += 1

    await message.answer(
        '<b>✅ Рассылка завершена!</b>\n'
        f'👤 Рассылку получили:  <code>{send_user}</code>\n'
        f'❌ Рассылку не получили:  <code>{exception_user}</code>'
    )
