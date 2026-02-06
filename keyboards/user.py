from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from data.database import *



def start_kb():
    keyboard = [[InlineKeyboardButton(text="Доступный ассортимент", callback_data="stock"),
                 InlineKeyboardButton(text="Поиск", callback_data="search")],
                [InlineKeyboardButton(text="Интересный факт", callback_data="fact"),
                 InlineKeyboardButton(text="Помощь", url="https://t.me/Imagisty")],
                [InlineKeyboardButton(text="Корзина", callback_data="cart")]]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def stock_kb():
    keyboard = []
    for category in await get_categories():
        keyboard.append([InlineKeyboardButton(text=f"{category}", callback_data=f"category_{ru_to_eng[category]}")])

    keyboard.append([InlineKeyboardButton(text="Назад", callback_data="menu")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)