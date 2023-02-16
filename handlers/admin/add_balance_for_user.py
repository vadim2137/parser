from aiogram import types
from aiogram.dispatcher.filters import Text

from data.config import ADMINS_ID
from loader import dp
from utils.db_commands import select_user, update_balance


@dp.message_handler(Text(startswith='/bal'), user_id=ADMINS_ID)
async def add_balance_for_user(message: types.Message):
    try:
        user = await select_user(int(message.text.split(' ')[1]))
        if user:
            await update_balance(
                int(message.text.split(' ')[1]),
                float(message.text.split(' ')[2])
            )
            await dp.bot.send_message(
                int(message.text.split(' ')[1]),
                f'<b>💸 Ваш баланс пополнен на сумму {float(message.text.split(" ")[2])} $!</b>'
            )
            await message.answer(
                f'<b>💸 Баланс пользователя [<code>{message.text.split(" ")[1]}</code>] пополнен '
                f'на сумму {float(message.text.split(" ")[2])} $!</b>'
            )
        else:
            await message.answer(
                '<b>❗️ Пользователь с таким ID не зарегистрирован в боте!</b>'
            )
    except ValueError:
        await message.answer('<b>❗️ Аргументы должны быть числом!</b>')
    except IndexError:
        await message.answer('<b>❗️ Аргументов должны быть всего 2!</b>')
