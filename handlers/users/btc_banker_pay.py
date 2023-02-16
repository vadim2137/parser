from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hlink

from data.config import ADMINS_ID
from keyboards import back_to_add_balance_kb
from loader import dp
from states import Banker
from utils import anti_flood
from utils.active_cheque_banker import get_btc_course, activate_cheque_banker
from utils.db_commands import update_balance, add_new_payment, update_payment_status, select_user, select_team


@dp.callback_query_handler(Text(equals='btc_banker'), state='*')
@dp.throttled(anti_flood, rate=2)
async def btc_banker_pay(call: types.CallbackQuery):
    await call.message.edit_caption(
        f'<b>{hlink("🤖 BTC Banker", "https://t.me/BTC_CHANGE_BOT")}</b>\n\n'
        f'— Курс: <b>Binance</b>\n'
        f'— Актуальный курс: <b>{await get_btc_course()}</b>\n\n'
        f'<b>💸 Пополните баланс отправив чек в чат</b>',
        reply_markup=back_to_add_balance_kb
    )
    await Banker.cheque.set()


@dp.message_handler(state=Banker.cheque)
@dp.throttled(anti_flood, rate=2)
async def check_banker_cheque(message: types.Message, state: FSMContext):
    if 'BTC_CHANGE_BOT?start=' in message.text:
        await message.answer('<b>♻️ Обработка чека...</b>')

        result = await activate_cheque_banker(message.text)
        if result == 'ErrorCheck':
            await message.answer('<b>Ой, извините 😕</b>')
        elif result == 'InvalidCheck':
            await message.answer('<b>❗️ Чек кто-то обналичил!</b>')
        else:
            await add_new_payment(
                result['code'],
                result['summa'],
                'Banker'
            )
            await update_payment_status(result['code'])
            await update_balance(message.from_user.id, result)
            await message.answer(
                f'<b>💸 Ваш баланс пополнен на сумму {result} $!</b>'
            )

            for admin in ADMINS_ID:
                await dp.bot.send_message(
                    admin,
                    f'<b>{hlink("🤖 BTC Banker", "https://t.me/BTC_CHANGE_BOT")}</b>\n'
                    f'<b>💸 Обнаружено пополнение от @{message.from_user.username} [<code>{message.from_user.id}</code>] '
                    f'на сумму {result} $!</b>'
                )
    else:
        await message.answer(
            '<b>❗️ Неправильный формат чека!</b>'
        )

    await state.reset_state(with_data=False)

