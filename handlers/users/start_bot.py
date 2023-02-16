from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, ChatTypeFilter, Text

from data.config import photo_1
from keyboards import start_kb, user_agreement_kb
from loader import dp
from utils import anti_flood
from utils.db_commands import select_user, update_user_is_agreed, select_all_subs
from utils.other import get_time_sub


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), CommandStart(), state='*')
@dp.throttled(anti_flood, rate=2)
async def start_bot(message: types.Message, state: FSMContext):
    user = await select_user(message.from_user.id)

    if user.is_agreed:
        subs_list = [f'– {sub.service}: ⏳ <code>{get_time_sub(sub.sub_seconds)}</code>' for sub in
                     await select_all_subs(message.from_user.id)]
        subs = '\n'.join(subs_list) if subs_list else '— Отсутствуют'
        await message.answer_photo(
            photo=photo_1,
            caption=f'<b>👋 Добро пожаловать в ADVANCED PARSER!</b>\n\n'
                    f'<b>🆔:</b> <code>{message.from_user.id}</code>\n'
                    f'<b>💵 Баланс:</b> <b>{user.balance} $</b>\n\n'
                    f'<b>🌟 Активные подписки:</b>\n{subs}',
            reply_markup=start_kb(message.from_user.id)
        )
    else:
        await message.answer_photo(
            photo=photo_1,
            caption=f'<b>👋 Добро пожаловать в ADVANCED PARSER!</b>',
            reply_markup=user_agreement_kb
        )

    await state.update_data(vt_work=False, wl_work=False, jg_work=False)
    await state.reset_state(with_data=False)


@dp.callback_query_handler(Text(equals='back_to_start'), state='*')
@dp.throttled(anti_flood, rate=1)
async def back_to_start(call: types.CallbackQuery, state: FSMContext):
    user = await select_user(call.from_user.id)
    if not user.is_agreed:
        await update_user_is_agreed(call.from_user.id)

    subs_list = [
        f'– {sub.service}: ⏳ <code>{get_time_sub(sub.sub_seconds)}</code>' for sub in
        await select_all_subs(call.from_user.id)
    ]
    subs = '\n'.join(subs_list) if subs_list else '— Отсутствуют'
    await call.message.edit_caption(
        caption=f'<b>👋 Добро пожаловать в ADVANCED PARSER!</b>\n\n'
                f'<b>🆔:</b> <code>{call.from_user.id}</code>\n'
                f'<b>💵 Баланс:</b> <b>{user.balance} $</b>\n\n'
                f'<b>🌟 Активные подписки:</b>\n{subs}',
        reply_markup=start_kb(call.from_user.id)
    )

    await state.reset_state(with_data=False)
