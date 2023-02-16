
from time import time
import os
from aiogram import types
from aiogram.dispatcher.filters import Text

from data.config import ADMINS_ID
from loader import dp


@dp.message_handler(Text(startswith='/proxy'), user_id=ADMINS_ID, state='*')
async def give_sub(message: types.Message):
    try:
        services = {
            'vt': '🌎 VINTED',
            'jg': '🇭🇺 JOFOGAS'
        }
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for service in services:
            markup.insert(
                types.KeyboardButton(text=f'{services[service]}')
            )
        await message.answer('Выбери сервис для замены прокси. Формат для прокси: user:pass@ip:port. 👇\n Заменить формат можно тут: \nhttps://buyproxies.org/panel/format.php', reply_markup=markup)
    except ValueError:
        await message.answer('<b>❗️ Аргументы должны быть числом!</b>')
    except IndexError:
        await message.answer('<b>❗️ Аргументов должны быть всего 2!</b>')


@dp.message_handler(Text(startswith='🌎 VINTED'), user_id=ADMINS_ID, state='*')
async def set_proxy_vt(message: types.Message):
    await message.answer('Отправьте файл с прокси для VINTED в формате: user:pass@ip:port. Назовите файл - vinted.txt')


@dp.message_handler(Text(startswith='🇭🇺 JOFOGAS'), user_id=ADMINS_ID, state='*')
async def set_proxy_jg(message: types.Message):
    await message.answer('Отправьте файл с прокси для JOFOGAS в формате: user:pass@ip:port. Назовите файл - jofogas.txt')


@dp.message_handler(Text(startswith='/vinted_p'), user_id=ADMINS_ID, state='*')
async def proxy_vt(message: types.Message):
    lines = message.text.split("\n")
    print(lines)
    is_valid = True
    for line in lines[1:-1]:
        if line == '/vinted_p':
            return
        parts = line.split(":")
        if len(parts) != 3:
            is_valid = False
            await message.answer('Неверный формат прокси. Используйте - user:pass@ip:port!')
            break
    
    if is_valid:
        file_path = "proxy/vinted.txt"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write("\n".join(message.text.split("\n")[1:-1]))
            await message.answer('Прокси успешно установлены для Vinted!')


@dp.message_handler(Text(startswith='/jofagas_p'), user_id=ADMINS_ID, state='*')
async def proxy_vt(message: types.Message):
    lines = message.text.split("\n")
    print(lines)
    is_valid = True
    for line in lines[1:-1]:
        if line == '/jofagas_p':
            return
        parts = line.split(":")
        if len(parts) != 3:
            is_valid = False
            await message.answer('Неверный формат прокси. Используйте - user:pass@ip:port!')
            break

    if is_valid:
        file_path = "proxy/jofagas.txt"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write("\n".join(message.text.split("\n")[1:-1]))
            await message.answer('Прокси успешно установлены для Jofagas!')

