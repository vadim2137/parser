import logging

from aiogram import executor

from filters import register_filters
from handlers import dp
from middlewares import register_middleware
from utils import set_default_commands
from utils.database import create_base


async def on_startup(dispatcher):
    register_middleware(dispatcher)
    register_filters(dispatcher)
    await set_default_commands(dispatcher)
    await create_base()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, on_startup=on_startup)
