from aiogram import types
from aiogram.dispatcher.filters import Text

from data.config import ADMINS_ID
from keyboards import interact_user, callback_interact
from loader import dp
from utils.db_commands import select_user, select_all_payments, select_all_subs, change_user_banned, delete_user
from utils.other import get_time_sub


@dp.message_handler(Text(startswith='/u'), user_id=ADMINS_ID)
async def get_user_stata(message: types.Message):
    try:
        user_id = int(message.text.split('/u')[1])
        user = await select_user(user_id)
        if user:
            payments = [payment.summa for payment in await select_all_payments(user_id)]
            subs_list = [f'– {sub.service}: ⏳ <code>{get_time_sub(sub.sub_seconds)}</code>' for sub in
                         await select_all_subs(user_id)]
            subs = '\n'.join(subs_list) if subs_list else '— Отсутствуют'

            await message.answer(
                f'<a href="tg://user?id={user_id}"><b>👤 {user.full_name}</b></a>\n\n'
                f'<b>🆔:</b> <code>{user_id}</code>\n'
                f'<b>💵 Баланс:</b> <b>{user.balance} $</b>\n'
                f'📅 Дата регистрации: <b>{user.date.date()}</b>\n\n'
                f'💳 Сумма пополнений: <b>{sum(payments)} $</b>\n'
                f'💳 Кол-во пополнений: <b>{len(payments)}</b>\n\n'
                f'<b>🌟 Активные подписки:</b>\n{subs}',
                reply_markup=interact_user(user_id, user.is_banned)
            )
        else:
            await message.answer(
                '<b>❗️ Пользователь с таким ID не зарегистрирован в боте!</b>'
            )
    except ValueError:
        await message.answer('<b>❗️ Аргументы должны быть числом!</b>')
    except IndexError:
        await message.answer('<b>❗️ Должен присутствовать 1 аргумент!</b>')


@dp.callback_query_handler(callback_interact.filter(action='delete'), user_id=ADMINS_ID)
async def ban_user(call: types.CallbackQuery, callback_data: dict):
    user_id = int(callback_data['user_id'])
    await delete_user(user_id)
    await call.message.edit_text('❗ Пользователь удалён')


@dp.callback_query_handler(callback_interact.filter(action=['ban', 'unban']), user_id=ADMINS_ID)
async def ban_user(call: types.CallbackQuery, callback_data: dict):
    user_id, is_banned = int(callback_data['user_id']), bool(int(callback_data['is_banned']))
    await change_user_banned(user_id, not is_banned)
    await call.message.edit_reply_markup(reply_markup=interact_user(user_id, not is_banned))
    if is_banned:
        await call.message.reply('<b>👍 Пользователь разблокирован</b>')
    else:
        await call.message.reply('<b>🤯 Пользователь заблокирован</b>')
