from time import time

from aiogram import types
from aiogram.dispatcher.filters import Text

from data.config import sub_tariffs, ADMINS_ID
from keyboards import back_to_parser_kb
from loader import dp
from utils.db_commands import select_user, update_balance, add_sub, select_all_subs
from utils.other import hours_to_days, hours_to_seconds


@dp.callback_query_handler(Text(startswith='sub'), state='*')
async def buy_sub(call: types.CallbackQuery):
    service = call.data.split('|')[2]
    subs = [sub.service for sub in await select_all_subs(call.from_user.id)]

    if service not in subs:
        user = await select_user(call.from_user.id)
        sub_hours = int(call.data.split('|')[1])

        if user.balance >= sub_tariffs[service][sub_hours][0]:
            await update_balance(call.from_user.id, float(-sub_tariffs[service][sub_hours][0]))
            await add_sub(call.from_user.id, int(time()) + hours_to_seconds(sub_hours), service, sub_hours)

            await call.message.edit_caption(
                f'<b>{service}</b>\n'
                f'<b>🎉 Вам выдана подписка на {hours_to_days(sub_hours)} дней!</b>',
                reply_markup=back_to_parser_kb
            )
            if user.ref_id != 0:
                summa = float(sub_tariffs[service][sub_hours][0]) * 0.2
                await update_balance(user.ref_id, summa)
                await dp.bot.send_message(
                    user.ref_id,
                    f'<b>💸 Ваш баланс пополнен на сумму {summa} $ от реферала '
                    f'<b>@{call.from_user.username}</b> [<code>{call.from_user.id}</code>]!</b>'
                )
        else:
            await call.answer(
                '❗️ На вашем балансе недостаточно средств!\n'
                '💡 Пополните баланс',
                show_alert=True
            )
    else:
        await call.answer(
            f'❗️ У вас уже есть подписка на {service}!',
            show_alert=True
        )
