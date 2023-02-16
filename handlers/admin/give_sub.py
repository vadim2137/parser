from time import time

from aiogram import types
from aiogram.dispatcher.filters import Text

from data.config import ADMINS_ID
from loader import dp
from utils.db_commands import select_user, add_sub, select_sub_per_service, update_sub_hours
from utils.other import hours_to_seconds


@dp.message_handler(Text(startswith='/sub'), user_id=ADMINS_ID, state='*')
async def give_sub(message: types.Message):
    try:
        split = message.text.split(' ')
        user = await select_user(int(split[1]))
        if user:
            services = {
                'vt': '🌎 VINTED',
                'wl': '🇪🇺 WALLAPOP',
                'jg': '🇭🇺 JOFOGAS'
            }
            if split[3] in services.keys():
                sub = await select_sub_per_service(int(split[1]), services[split[3]])

                if sub and sub.sub_seconds - int(time()) > 0:
                    await update_sub_hours(
                        sub.id,
                        hours_to_seconds(int(split[2])),
                        int(split[2])
                    )
                else:
                    await add_sub(
                        int(split[1]),
                        time() + hours_to_seconds(int(split[2])),
                        services[split[3]],
                        int(split[2]),
                        True
                    )

                await dp.bot.send_message(
                    int(split[1]),
                    f'<b>{services[split[3]]}</b>\n'
                    f'<b>🎉 Вам выдана подписка на {split[2]} часов!</b>'
                )
                await message.answer(
                    f'<b>🌟 Пользователю [<code>{split[1]}</code>] выдана подписка на '
                    f'{split[2]} часов ({services[split[3]]})</b>'
                )
            else:
                await message.answer(
                    f'<b>❗️ Сервис <code>{split[3]}</code> не существует!</b>\n'
                    f'<b>Доступные сервисы:</b>\n'
                    f'{services}'
                )
        else:
            await message.answer(
                '<b>❗️ Пользователь с таким ID не зарегистрирован в боте!</b>'
            )
    except ValueError:
        await message.answer('<b>❗️ Аргументы должны быть числом!</b>')
    except IndexError:
        await message.answer('<b>❗️ Аргументов должны быть всего 2!</b>')
