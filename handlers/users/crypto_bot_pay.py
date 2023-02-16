from aiocryptopay import AioCryptoPay
from aiocryptopay.exceptions import CryptoPayAPIError
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hlink

from data.config import ADMINS_ID, CRYPTO_PAY_TOKEN, photo_1
from keyboards.inline.payments_kb import check_crypto_bot_kb, crypto_bot_currencies_kb, back_to_add_balance_kb
from loader import dp
from states import CryproBot
from utils.cryptobot_pay import check_crypto_bot_invoice, get_crypto_bot_sum
from utils.db_commands import select_payment, update_balance, add_new_payment, update_payment_status


@dp.callback_query_handler(Text('crypto_bot'), state='*')
async def crypto_bot_pay(call: types.CallbackQuery):
    await call.message.edit_caption(
        f'<b>{hlink("⚜️ CryptoBot", "https://t.me/CryptoBot")}</b>\n\n'
        '— Минимум: <b>0.1 $</b>\n\n'
        f'<b>💸 Введите сумму пополнения в долларах</b>',
        reply_markup=back_to_add_balance_kb
    )
    await CryproBot.sum.set()


@dp.message_handler(state=CryproBot.sum)
async def crypto_bot_sum(message: types.Message, state: FSMContext):
    try:
        if float(message.text) >= 0.1:
            await message.answer(
                f'<b>{hlink("⚜️ CryptoBot", "https://t.me/CryptoBot")}</b>\n\n'
                f'— Сумма: <b>{message.text} $</b>\n\n'
                '<b>💸 Выберите валюту, которой хотите оплатить счёт</b>',
                disable_web_page_preview=True,
                reply_markup=crypto_bot_currencies_kb()
            )
            await state.update_data(crypto_bot_sum=float(message.text))
            await CryproBot.currency.set()
        else:
            await message.answer(
                '<b>⚠️ Минимум: 0.1 $!<b>'
            )
    except ValueError:
        await message.answer(
            '<b>❗️Сумма для пополнения должна быть в числовом формате!</b>'
        )


@dp.callback_query_handler(Text(startswith='crypto_bot_currency'), state=CryproBot.currency)
async def crypto_bot_currency(call: types.CallbackQuery, state: FSMContext):
    try:
        await call.message.delete()
        data = await state.get_data()
        cryptopay = AioCryptoPay(CRYPTO_PAY_TOKEN)
        invoice = await cryptopay.create_invoice(
            asset=call.data.split('|')[1],
            amount=await get_crypto_bot_sum(
                data['crypto_bot_sum'],
                call.data.split('|')[1]
            )
        )
        await cryptopay.close()
        await state.update_data(crypto_bot_currency=call.data.split('|')[1])
        await add_new_payment(call.from_user.id, str(invoice.invoice_id), data['crypto_bot_sum'], 'CryptoBot')
        await call.message.answer_photo(
            photo=photo_1,
            caption=f'<b>💸 Отправьте {data["crypto_bot_sum"]} $ {hlink("по ссылке", invoice.pay_url)}</b>',
            reply_markup=check_crypto_bot_kb(invoice.pay_url, invoice.invoice_id)
        )
        await state.reset_state(with_data=False)
    except CryptoPayAPIError:
        await call.message.answer(
            '<b>⚠️ Произошла ошибка!</b>'
        )


@dp.callback_query_handler(Text(startswith='check_crypto_bot'), state='*')
async def check_crypto_bot(call: types.CallbackQuery):
    payment_id = call.data.split('|')[1]
    payment = await select_payment(payment_id)
    if not payment.status:
        if await check_crypto_bot_invoice(int(payment_id)):
            await update_payment_status(payment_id)
            await update_balance(call.from_user.id, payment.summa)

            await call.answer(
                '✅ Оплата прошла успешно!',
                show_alert=True
            )
            await call.message.delete()
            await call.message.answer(
                f'<b>💸 Ваш баланс пополнен на сумму {payment.summa} $!</b>'
            )

            for admin in ADMINS_ID:
                await call.bot.send_message(
                    admin,
                    f'<b>{hlink("⚜️ CryptoBot", "https://t.me/CryptoBot")}</b>\n'
                    f'<b>💸 Обнаружено пополнение от @{call.from_user.username} [<code>{call.from_user.id}</code>] '
                    f'на сумму {payment.summa} $!</b>'
                )
        else:
            await call.answer(
                '❗️ Вы не оплатили счёт!',
                show_alert=True
            )
