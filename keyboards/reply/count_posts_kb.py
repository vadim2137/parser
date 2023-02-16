from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

count_posts = ['3', '5', '10']
count_reviews = ['0', '3', '5']

count_views = ['300', '500', '1000']


def count_posts_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in count_posts:
        markup.insert(
            KeyboardButton(text=text)
        )
    return markup


def count_reviews_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in count_reviews:
        markup.insert(
            KeyboardButton(text=text)
        )
    return markup


def count_views_kb():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for text in count_views:
        markup.insert(
            KeyboardButton(text=text)
        )
    return markup
