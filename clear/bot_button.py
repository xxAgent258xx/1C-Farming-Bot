from aiogram.filters import CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from bot_param import param2
from bot_const import (select_from_db, Form1, Form2, Form3, Form4, get_promo,
                       insert_into_db, main_keyboard, time_keyboard, START_TEXT,
                       CMD_TEXT)
from bot_upgrade import upgrade
from bot_name import naming
from bot_collect import collect
from bot_time import timezone
from bot_promo import activate


async def upgrade_button(message: Message, state: FSMContext):
    num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
    if num is None:
        num = 0
    await message.reply(f"Введите номер {param2[1]} и номер характеристики через пробел. Всего у вас: {num}{param2[13]}",
                        reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form1.value)


async def process_upgrade_button(message: Message, state: FSMContext):
    form = await state.update_data(value=message.text)
    max_num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
    if max_num is None:
        max_num = 0
    num: str = form['value']
    if len(num.split()) >= 2:
        p1 = num.split()[0]
        p2 = num.split()[1]
        await upgrade(message, p1, p2)
    else:
        await message.reply("Недостаточно значений❌",
                            reply_markup=main_keyboard)
    await state.clear()


async def name_button(message: Message, state: FSMContext):
    max_num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
    if max_num is None:
        max_num = 0
    await message.reply(f"Введите номер {param2[1]} и имя через пробел. Всего у вас: {max_num}{param2[13]}",
                        reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form2.value)


async def process_name_button(message: Message, state: FSMContext):
    form = await state.update_data(value=message.text)
    max_num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
    if max_num is None:
        max_num = 0
    num: str = form['value']
    if len(num.split()) >= 2:
        id_ = num.split()[0]
        name_ = num.split()[1]
        await naming(message, id_, name_)
    else:
        await message.reply("Недостаточно значений❌",
                            reply_markup=main_keyboard)
    await state.clear()


async def collect_button(message: Message, state: FSMContext):
    max_num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
    if max_num is None:
        max_num = 0
    await message.reply(f"Введите номер {param2[1]}. Всего у вас: {max_num}{param2[13]}",
                        reply_markup=ReplyKeyboardRemove())
    await state.set_state(Form3.value)


async def process_collect_button(message: Message, state: FSMContext):
    form = await state.update_data(value=message.text)
    max_num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
    if max_num is None:
        max_num = 0
    num: str = form['value']
    id_ = num.split()[0]
    await collect(message, id_)
    await state.clear()


async def time_button(message: Message, state: FSMContext):
    await message.reply("Выберите свой часовой пояс из списка",
                        reply_markup=time_keyboard)
    await state.set_state(Form4.value)


async def process_time_button(message: Message, state: FSMContext):
    form = await state.update_data(value=message.text)
    num: str = form['value']
    zones = [y[0].text for y in (x for x in time_keyboard.keyboard)] + [y[1].text for y in (x for x in time_keyboard.keyboard)]
    if num in zones:
        num = str(int(num.split()[0][3:]) - 3)
        await timezone(message, num)
    else:
        await message.reply("Неверное значение",
                            reply_markup=main_keyboard)
    await state.clear()


"""Стартовое сообщение с списком команд"""


async def start(message: Message, command: CommandObject = CommandObject()) -> None:
    if len(await select_from_db(f'SELECT * FROM stat WHERE user_id={message.from_user.id}')) == 0:
        """Запись нового пользователя"""
        await insert_into_db(
            f"INSERT INTO stat(user_id, kol, koff, gets_kol, time, streak, activity) VALUES ({message.from_user.id}, 0, 0, 0, 0, 1, 0)")

    await message.reply(START_TEXT, reply_markup=main_keyboard)

    """Проверка на наличие промокода"""
    if command.args:
        if not ((await get_promo(command.args)) is None):
            await activate(message, promo=command.args)