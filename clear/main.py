import asyncio
import logging
from aiogram import F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove, InlineQuery
from aiogram.fsm.context import FSMContext

from bot_const import (bot, dp, main_keyboard, select_from_db, Form1, Form2,
                       Form3, Form4, CMD_TEXT, cancel_keyboard)

# from bot_param import param1, param2, param3, names, values1, values2, values3, price
from bot_get import get
from bot_buy import buy
from bot_upgrade import upgrade
from bot_collect import collect
from bot_name import naming
from bot_promo import activate
from bot_time import timezone
from bot_profile import me
from bot_admin import new_admin, select, execute
from bot_sell import sell, inline, market
from bot_button import (upgrade_button, process_upgrade_button, name_button,
                        process_name_button, collect_button, time_button,
                        process_collect_button, process_time_button, start)

logging.basicConfig(level=logging.INFO)


@dp.message(F.text == cancel_keyboard.keyboard[0][0].text)
async def cancel(message: Message, state: FSMContext):
    await message.reply("Действие отменено. Список команд: /menu", reply_markup=main_keyboard)
    await state.clear()


"""Прокачка легендарного персонажа"""


@dp.message(Command(commands=['upgrade']))
async def upgrade_main(message: Message, p1="", p2="") -> None:
    await upgrade(message, p1, p2)


"""Сделать персонажа коллекционным"""


@dp.message(Command(commands=['collect', 'collectible', 'collected']))
async def collect_main(message: Message, num_="") -> None:
    await collect(message, num_)


"""Присвоение имени легендарному персонажу"""


@dp.message(Command(commands=['name']))
async def naming_main(message: Message, id_="", name_="") -> None:
    await naming(message, id_, name_)


"""Смена часового пояса"""


@dp.message(Command(commands=['time', 'timezone', 'set_time']))
async def timezone_main(message: Message, timer="") -> None:
    await timezone(message, timer)


"""Активация промокода"""


@dp.message(Command(commands=['promo', 'promocode', 'activate']))
async def activate_main(message: Message, promo="") -> None:
    await activate(message, promo)


@dp.message(Command(commands=['new_admin', 'add_admin']))
async def new_admin_main(message: Message) -> None:
    await new_admin(message)


@dp.message(Command(commands=['execute', 'script', 'insert']))
async def execute_main(message: Message) -> None:
    await execute(message)


@dp.message(Command(commands=['select']))
async def select_main(message: Message) -> None:
    await select(message)


"""Обработка кнопок (помещена в конец файла т.к. пользователь может передумать и воспользоваться командой)"""


@dp.message(Command(commands=['menu']))
@dp.message(F.text == main_keyboard.keyboard[4][0].text)
async def start_button(message: Message):
    await message.reply(CMD_TEXT, reply_markup=main_keyboard)


@dp.message(F.text == main_keyboard.keyboard[2][0].text)
async def upgrade_button_main(message: Message, state: FSMContext):
    await upgrade_button(message, state)


@dp.message(Form1.value)
async def process_upgrade_button_main(message: Message, state: FSMContext):
    await process_upgrade_button(message, state)


@dp.message(F.text == main_keyboard.keyboard[2][1].text)
async def name_button_main(message: Message, state: FSMContext):
    await name_button(message, state)


@dp.message(Form2.value)
async def process_name_button_main(message: Message, state: FSMContext):
    await process_name_button(message, state)


@dp.message(F.text == main_keyboard.keyboard[3][0].text)
async def collect_button_main(message: Message, state: FSMContext):
    await collect_button(message, state)


@dp.message(Form3.value)
async def process_collect_button_main(message: Message, state: FSMContext):
    await process_collect_button(message, state)


@dp.message(F.text == main_keyboard.keyboard[4][1].text)
async def time_button_main(message: Message, state: FSMContext):
    await time_button(message, state)


@dp.message(Form4.value)
async def process_time_button_main(message: Message, state: FSMContext):
    await process_time_button(message, state)


"""Стартовое сообщение с списком команд"""


@dp.message(CommandStart())
@dp.message(F.text == main_keyboard.keyboard[0][0].text)
async def start_main(message: Message, command: CommandObject = CommandObject()) -> None:
    await start(message, command)


@dp.message(F.text == main_keyboard.keyboard[0][1].text)
async def turn_down(message: Message):
    await message.reply("Клавиатура скрыта.", reply_markup=ReplyKeyboardRemove())


"""Получение валюты"""


@dp.message(F.text == main_keyboard.keyboard[1][0].text)
@dp.message(Command(commands=['get']))
async def get_main(message: Message) -> None:
    await get(message)


"""Покупка легендарного персонажа"""


@dp.message(F.text == main_keyboard.keyboard[1][1].text)
@dp.message(Command(commands=['buy']))
async def buy_main(message: Message, promo=0) -> None:
    await buy(message, promo)


"""Профиль"""


@dp.message(F.text == main_keyboard.keyboard[3][1].text)
@dp.message(Command(commands=['me']))
async def me_main(message: Message) -> None:
    await me(message)


@dp.message(Command(commands=['sell']))
async def sell_main(message: Message) -> None:
    await sell(message)


@dp.message(Command(commands=['market']))
async def market_main(message: Message) -> None:
    await market(message)


@dp.inline_query()
async def inline_main(inline_query: InlineQuery):
    await inline(inline_query)


async def on_startup():
    bot_info = await bot.get_me()
    cursor = await select_from_db('SELECT * FROM admins')
    for ADMIN in cursor:
        if ADMIN[1]:
            await bot.send_message(ADMIN[0], f'Бот @{bot_info.username} включён')


async def on_shutdown():
    bot_info = await bot.get_me()
    cursor = await select_from_db('SELECT * FROM admins')
    for ADMIN in cursor:
        if ADMIN[1]:
            await bot.send_message(ADMIN[0], f'Бот @{bot_info.username} выключен')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
