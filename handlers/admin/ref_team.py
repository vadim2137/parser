from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.utils.deep_linking import get_start_link

from data.config import photo_1
from keyboards.inline.teams_kb import teams_kb, team_kb, back_to_teams
from loader import dp
from states import CreateTeam
from utils.db_commands import select_all_teams, add_new_team, select_team, select_count_ref_team_users, \
    select_count_ref_team_users_per_date, select_sum_payments_per_service, select_user, delete_team


@dp.callback_query_handler(Text('team_ref'), state='*')
async def team_ref(call: types.CallbackQuery):
    teams = await select_all_teams()
    caption = '<b>👇 Выберите тиму:</b>' if teams else '<b>❗️ У вас нет тим!</b>'
    await call.message.edit_caption(
        caption,
        reply_markup=teams_kb(teams)
    )


@dp.callback_query_handler(Text(startswith='team'), state='*')
async def team_info(call: types.CallbackQuery):
    await call.answer('⏳ Собираю статистику...')
    team_id = int(call.data.split('|')[1])
    team = await select_team(team_id)
    if team:
        # banker_payments_sum = sum(
        #     [payment.summa for payment in await select_sum_payments_per_service('Banker')
        #      if (await select_user(payment.user_id)).team_id != 0 and
        #      await select_team((await select_user(payment.user_id)).team_id)
        #      ]
        # )
        crypto_bot_payments_sum = list()
        for payment in await select_sum_payments_per_service('CryptoBot'):
            pay_user = await select_user(payment.user_id)
            if pay_user and pay_user.team_id == team_id:
                crypto_bot_payments_sum.append(payment.summa)

        await call.message.edit_caption(
            f'<b>{team.team_name}</b>\n'
            f'👥 Приглашено: <b>{await select_count_ref_team_users(team.id)}</b>\n'
            f'📅 За последние 30 дней: <b>{(await select_count_ref_team_users_per_date(team.id, 30))}</b>\n\n'
            f'<b>💵 Пополнения:</b>\n'
            f'⚜️ CryptoBot: <b>{sum(crypto_bot_payments_sum)} $</b>\n\n'
            f'🔗 Реферальная ссылка:\n{(await get_start_link(f"team{team.id}"))}',
            reply_markup=team_kb(team.id)
        )


@dp.callback_query_handler(Text(startswith='del_team'), state='*')
async def dl_team(call: types.CallbackQuery):
    await delete_team(int(call.data.split('|')[1]))
    await call.answer('❌ Тима удалена!')
    teams = await select_all_teams()
    caption = '<b>👇 Выберите тиму:</b>' if teams else '<b>❗️ У вас нет тим!</b>'
    await call.message.edit_caption(
        caption,
        reply_markup=teams_kb(teams)
    )


@dp.callback_query_handler(Text('new_team'), state='*')
async def new_team(call: types.CallbackQuery):
    await call.message.edit_caption(
        '<b>👇 Введите название для тимы:</b>',
        reply_markup=back_to_teams
    )
    await CreateTeam.name.set()


@dp.message_handler(state=CreateTeam.name)
async def new_team_name(message: types.Message):
    await add_new_team(message.text)
    await message.answer(f'✅ Тима <b>{message.text}</b> успешно добавлена!')
    await message.answer_photo(
        photo=photo_1,
        caption='<b>👇 Выберите тиму:</b>',
        reply_markup=teams_kb(await select_all_teams())
    )
