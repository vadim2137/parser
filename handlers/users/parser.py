from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, ChatTypeFilter
from aiogram.types import ReplyKeyboardRemove, InputFile

from keyboards import market_places_kb
from keyboards.inline.statistics import stats_callback
from loader import dp
from utils import anti_flood
from utils.db_commands import select_user


@dp.callback_query_handler(Text(equals='parser'), state='*')
@dp.throttled(anti_flood, rate=1)
async def parser(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(vt_work=False, wl_work=False, jg_work=False)
    user = await select_user(call.from_user.id)
    if user:
        await call.message.edit_caption(
            '<b>🛍 Выберите площадку:</b>',
            reply_markup=market_places_kb
        )


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), Text(equals='⛔️ Остановить парсер'), state='*')
@dp.throttled(anti_flood, rate=1)
async def stop_parser(message: types.Message, state: FSMContext):
    await message.answer('⛔️ Останавливаю парсер...', reply_markup=ReplyKeyboardRemove())
    await state.update_data(vt_work=False, wl_work=False, jg_work=False)

    await state.reset_state(with_data=False)


@dp.callback_query_handler(stats_callback.filter(), state='*')
@dp.throttled(anti_flood, rate=1)
async def stop_parser(call: types.CallbackQuery, callback_data: dict):
    file_name = callback_data['file_id']
    await call.message.answer_document(
        caption='📊 Таблица с данными об объявлениях',
        document=InputFile(f'history/{file_name}.csv')
    )
    await call.answer()
