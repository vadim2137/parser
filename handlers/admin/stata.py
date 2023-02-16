from aiogram import types
from aiogram.dispatcher.filters import Text

from keyboards import back_to_admin_kb
from loader import dp
from utils.db_commands import select_count_users, select_count_users_with_subs, select_count_users_per_date, \
    select_count_subs_per_service_and_sub_hours, select_sum_payments_per_service


@dp.callback_query_handler(Text(equals='stata'), state='*')
async def stata(call: types.CallbackQuery):
    await call.answer('⏳ Собираю статистику...')
    count_users_with_sub = 0
    user_ids = list()
    for sub in await select_count_users_with_subs():
        if sub.user_id not in user_ids:
            count_users_with_sub += 1
            user_ids.append(sub.user_id)

    # banker_payments_sum = sum([payment.summa for payment in await select_sum_payments_per_service("Banker")])
    crypto_bot_payments_sum = sum([payment.summa for payment in await select_sum_payments_per_service("CryptoBot")])

    await call.message.edit_caption(
        f'<b>📊️ Статистика</b>\n'
        f'👥 Пользователей: <b>{(await select_count_users())}</b>\n'
        f'🌟 Активных пользователей: <b>{count_users_with_sub}</b>\n'
        f'📅 За последние 30 дней: <b>{(await select_count_users_per_date(30))}</b>\n\n'
        f'<b>💵 Пополнения:</b>\n'
        f'⚜️ CryptoBot: <b>{crypto_bot_payments_sum} $</b>\n\n'
        f'<b>🌎 VINTED:</b>\n'
        f'- 1 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🌎 VINTED", 24))} раз</b>\n'
        f'- 3 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🌎 VINTED", 72))} раз</b>\n'
        f'- 7 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🌎 VINTED", 168))} раз</b>\n'
        f'- 15 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🌎 VINTED", 360))} раз</b>\n'
        f'- 31 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🌎 VINTED", 744))} раз</b>\n\n'
        f'<b>🇪🇺 WALLAPOP:</b>\n'
        f'- 1 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🇪🇺 WALLAPOP", 24))} раз</b>\n'
        f'- 3 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🇪🇺 WALLAPOP", 72))} раз</b>\n'
        f'- 7 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🇪🇺 WALLAPOP", 168))} раз</b>\n'
        f'- 15 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🇪🇺 WALLAPOP", 360))} раз</b>\n'
        f'- 31 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🇪🇺 WALLAPOP", 744))} раз</b>\n\n'
        f'<b>🇭🇺 JOFOGAS</b>\n'
        f'- 1 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🇭🇺 JOFOGAS", 24))} раз</b>\n'
        f'- 3 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🇭🇺 JOFOGAS", 72))} раз</b>\n'
        f'- 7 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🇭🇺 JOFOGAS", 168))} раз</b>\n'
        f'- 15 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🇭🇺 JOFOGAS", 360))} раз</b>\n'
        f'- 31 day куплено: <b>{(await select_count_subs_per_service_and_sub_hours("🇭🇺 JOFOGAS", 744))} раз</b>\n\n',
        reply_markup=back_to_admin_kb
    )
