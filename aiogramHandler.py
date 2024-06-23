import hashlib

import asyncio

import siteHandler
from database import Database

import requests
# import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.helper import Helper, HelperMode, ListItem
# from aiogram.fsm.content import FSMContext

API_TOKEN = ''
solt = ""

class Events(Helper):
    mode = HelperMode.snake_case

    MAIN_MENU = ListItem()
    SELECT_RECTANGLE = ListItem()
    SHOW_RECTANGLE = ListItem()
    WAIT_SELECT_RECTANGLE = ListItem()

# logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(Bot(token=API_TOKEN, parse_mode="HTML"), storage=MemoryStorage())
# dp.middleware.setup(LoggingMiddleware())
Events = Events

DB = Database()

@dp.message_handler(commands="start")
async def start(message: types.Message):
    telegram_id = f"'{message.from_user.id}'"
    hash_id = f"'{hashlib.sha256((solt+str(telegram_id)).encode()).hexdigest()}'"
    DB.add_user(telegram_id, hash_id)

    await message.answer("Добрый день. Это бот для создания картин, состоящих из дорог.")
    await main_menu(message)

@dp.message_handler(state=Events.MAIN_MENU[0], text=["Создать картину"])
async def select_rectangle(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(Events.WAIT_SELECT_RECTANGLE[0])

    telegram_id = message.from_user.id
    hash_id = DB.get_hash(telegram_id)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create_map = types.KeyboardButton(text="Отменить")
    keyboard.add(create_map)

    await message.answer(f"Супер! \n\n Теперь вам нужно перейти по этой ссылке и выбрать участок, который"
                         "вы хотите увидеть на своей картине \n\n"
                         f"http://127.0.0.1:5000?hash={hash_id[0]} \n\n"
                         f"После подтверждения на сайте здесь появятся дальнейшие инструкции.\n\n"
                         f"Для отмены нажмите на кнопку отмены", reply_markup=keyboard)

@dp.message_handler(state=Events.MAIN_MENU[0])
@dp.message_handler(state=Events.WAIT_SELECT_RECTANGLE[0], text=["Отменить"])
async def main_menu(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(Events.MAIN_MENU[0])

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create_map = types.KeyboardButton(text="Создать картину")
    keyboard.add(create_map)

    await message.answer("Нажмите на кнопку для создания картины", reply_markup=keyboard)

@dp.message_handler(state=Events.WAIT_SELECT_RECTANGLE[0])
async def cancel(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    create_map = types.KeyboardButton(text="Отменить")
    keyboard.add(create_map)

    await message.answer("Для отмены нажмите на кнопку отмены", reply_markup=keyboard)


async def send_pic(hash_id, path_to_osm, path_to_pic):
    telegram_id = DB.get_telegram_id(f"'{hash_id}'")[0]
    state = dp.current_state(user=telegram_id)

    await state.set_state(Events.MAIN_MENU[0])
    user_id = DB.get_user_id(f"'{hash_id}'")[0]
    DB.add_pictures(user_id, f"'{path_to_osm}'", f"'{path_to_pic}'")

    message = "Вот ваша картина"
    await bot.send_message(chat_id=telegram_id, text=message)
    file = types.InputFile(path_to_pic)
    a = await bot.send_document(chat_id=telegram_id, document=file)
    await main_menu(a)

async def get_user_state(hash_id):
    telegram_id = DB.get_telegram_id(f"'{hash_id}'")[0]
    state = await dp.current_state(user=telegram_id).get_state()
    return state

async def startup(dispatcher: Dispatcher):
    aiohttp_server = asyncio.create_task(siteHandler.start())
    await aiohttp_server

def start():
    # DB.drop_table_users()
    # DB.drop_table_pictures()
    DB.create_table_users()
    DB.create_table_pictures()
    executor.start_polling(dp, on_startup=startup ,skip_updates=True)
