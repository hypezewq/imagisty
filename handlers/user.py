from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from keyboards.user import *
from data.database import *
from classes.paginator import Paginator

user_router = Router()


class Search(StatesGroup):
    search_text = State()


@user_router.message(Command("start"))
async def cmd_start(message: Message):
    await message.delete()
    await message.answer("Добро пожаловать в магазин автозапчастей", reply_markup=start_kb())


@user_router.callback_query(F.data == "menu")
async def start(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("Добро пожаловать в магазин автозапчастей", reply_markup=start_kb())


@user_router.callback_query(F.data == "stock")
async def stock_callback(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("Выберите категорию", reply_markup=await stock_kb())


@user_router.callback_query(F.data.startswith("category_"))
async def category_callback(call: CallbackQuery):
    await call.answer()
    paginator = Paginator(
        objects=await get_autoparts_by_category(eng_to_ru[call.data.split("_")[-1]]),
        get_button_text_from_object_func=lambda autopart, index: f"{autopart.name}",
        get_callback_data_from_object_func=lambda autopart,
                                                  index: f"autopart_{autopart.id}:category_{call.data.split("_")[-1]}",
        ending_kb_elements=[[InlineKeyboardButton(text="Назад", callback_data="stock")]]
    )
    await paginator.edit_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        bot_instance=call.bot
    )


@user_router.callback_query(F.data == "fact")
async def send_fact(call: CallbackQuery):
    from random import choice
    await call.answer()
    with open("100_facts_about_cars.txt", encoding="utf-8") as f:
        s = f.readlines()

    await call.message.answer(text=choice(s).strip())


@user_router.callback_query(F.data.startswith("autopart_"))
async def autopart_callback(call: CallbackQuery):
    await call.answer()
    autopart = await get_autopart(call.data.split(":")[0].split("_")[-1])
    msg = (f"{autopart.name}\n\n"
           f"Код товара: {autopart.code}\n"
           f"Произведено: {autopart.production}\n"
           f"Артикул: {autopart.article if autopart.article else "-"}\n"
           f"Цена: {autopart.cost} ₽\n"
           f"Категория: {autopart.category}\n")
    await call.message.edit_text(text=msg, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Добавить в корзину", callback_data=f"add_to_cart:{autopart.id}"),
                          InlineKeyboardButton(text="Назад",
                                               callback_data=f"category_{(call.data.split(':')[-1]).split('_')[-1]}"), ]]))


@user_router.callback_query(F.data == "search")
async def search_callback(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text(text="Введите, то что хотите найти")
    await state.set_state(Search.search_text)
    await state.update_data(call=call)


@user_router.message(Search.search_text)
async def search_message(message: Message, state: FSMContext):
    await message.delete()
    call = await state.get_value("call")
    paginator = Paginator(
        objects=await get_autoparts_by_name(message.text),
        get_button_text_from_object_func=lambda autopart, index: f"{autopart.name}",
        get_callback_data_from_object_func=lambda autopart,
                                                  index: f"autopart_{autopart.id}:category_{ru_to_eng[autopart.category]}",
        ending_kb_elements=[[InlineKeyboardButton(text="В меню", callback_data="menu")]]

    )
    await paginator.edit_message(
        chat_id=message.chat.id,
        message_id=call.message.message_id,
        bot_instance=message.bot
    )


@user_router.callback_query(F.data.startswith("add_to_cart:"))
async def add_to_cart_callback(call: CallbackQuery, state: FSMContext):
    await call.answer(f"Товар успешно добавлен в корзину")
    cart = await state.get_value("cart")
    print(cart)
    if not cart:
        await state.update_data(cart=[int(call.data.split(":")[-1])])
    else:
        cart.append(int(call.data.split(":")[-1]))
        await state.update_data(cart=cart)


@user_router.callback_query(F.data == "cart")
async def open_cart_callback(call: CallbackQuery, state: FSMContext):
    if await state.get_value("cart"):
        cart = await get_cart(await state.get_value("cart"))
        await call.answer()
        paginator = Paginator(
            objects=cart,
            get_button_text_from_object_func=lambda autopart, index: f"{autopart.name}",
            get_callback_data_from_object_func=lambda autopart, index: f"cart:{autopart.id}",
            formatted_text_for_page=f"Итоговая цена: {sum(map(lambda x: x.cost, cart))} ₽",
            ending_kb_elements=[[InlineKeyboardButton(text="Меню", callback_data="menu")]]
        )

        await paginator.edit_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            bot_instance=call.bot
        )
    else:
        await call.answer("Корзина пуста")

@user_router.callback_query(F.data.startswith("delete_from_cart:"))
async def delete_from_cart_callback(call: CallbackQuery, state: FSMContext):
    cart = await get_cart(await state.get_value("cart"))
    c = False
    s = []
    for i in cart:
        if i.id == int(call.data.split(":")[-1]) and not c:
            c = True
            continue
        else:
            s.append(i.id)

    await state.update_data(cart=s)
    await call.answer("Товар успешно удален из корзины")
    if s:
        await open_cart_callback(call=call, state=state)
    else:
        await start(call)


@user_router.callback_query(F.data.startswith("cart:"))
async def cart_callback(call: CallbackQuery, state: FSMContext):
    await call.answer()
    autopart = await get_autopart(int(call.data.split(":")[-1]))
    msg = (f"{autopart.name}\n\n"
           f"Код товара: {autopart.code}\n"
           f"Произведено: {autopart.production}\n"
           f"Артикул: {autopart.article if autopart.article else "-"}\n"
           f"Цена: {autopart.cost} ₽\n"
           f"Категория: {autopart.category}\n")
    await call.message.edit_text(text=msg, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Удалить из корзины", callback_data=f"delete_from_cart:{autopart.id}"),
             InlineKeyboardButton(text="Назад", callback_data=f"cart" if await state.get_value("cart") else "menu"), ]]))
