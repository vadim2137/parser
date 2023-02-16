from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

stats_callback = CallbackData("stats", "file_id")


def statistics(file_id: str):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="📊 Да", callback_data=stats_callback.new(file_id)))
    return keyboard
