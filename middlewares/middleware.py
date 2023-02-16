from aiogram import Dispatcher, types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from data.config import GROUP_ID, photo_1, ADMINS_ID
from keyboards.inline.sub_channel_kb import sub_chanel_kb
from loader import dp
from utils.db_commands import check_args, register_user, add_log_filter, select_team


class SubMiddleware(BaseMiddleware):
    async def on_process_message(self, message: Message, data: dict):
        if message.content_type == types.ContentType.TEXT and '/start' in message.text:
            args = await check_args(message.get_args(), message.from_user.id)
            await register_user(
                message.from_user.id,
                message.from_user.full_name,
                args['ref'],
                args['team']
            )
            await add_log_filter(message.from_user.id)

            if args['ref'] != 0 and args['ref'] != message.from_user.id:
                await dp.bot.send_message(
                    args['ref'],
                    f'🤖 По вашей ссылке зарегистрировался новый реферал!\n'
                    f'👤 Реферал: <b>@{message.from_user.username}</b> [<code>{message.from_user.id}</code>]'
                )
            elif args['team'] != 0:
                for admin in ADMINS_ID:
                    await dp.bot.send_message(
                        admin,
                        f'🤖 Зарегистрировался новый реферал от <b>{(await select_team(args["team"])).team_name}</b>!\n'
                        f'👤 Реферал: <b>@{message.from_user.username}</b> [<code>{message.from_user.id}</code>]'
                    )

        sub = await dp.bot.get_chat_member(GROUP_ID, message.from_user.id)
        if sub.status == types.ChatMemberStatus.LEFT:
            await message.answer_photo(
                photo=photo_1,
                caption='<b>❗️ Подпишитесь на новостной канал, чтобы продолжить</b>',
                reply_markup=sub_chanel_kb
            )
            raise CancelHandler

    async def on_process_callback_query(self, call: CallbackQuery, data: dict):
        sub = await dp.bot.get_chat_member(GROUP_ID, call.from_user.id)
        if sub.status == types.ChatMemberStatus.LEFT:
            await call.answer(
                '❗️ Вы не подписаны на новостной канал!',
                show_alert=True
            )
            if call.message.caption != '❗️ Подпишитесь на новостной канал, чтобы продолжить':
                await call.message.edit_caption(
                    caption='<b>❗️ Подпишитесь на новостной канал, чтобы продолжить</b>',
                    reply_markup=sub_chanel_kb
                )
            raise CancelHandler


def register_middleware(dp: Dispatcher):
    dp.middleware.setup(SubMiddleware())
