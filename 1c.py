import asyncio
import logging
from aiogram import F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove, InlineQuery
from aiogram.fsm.context import FSMContext

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
    lvl_up = False
    maybe = False
    have_bonus = False
    bonus = 0
    DELTA = 2
    streak = 1
    h2 = ""

    """Получение значений из БД"""
    user = await select_from_db(
        f"SELECT kol, last, gets_kol, koff, time, bonus_date, promo FROM stat WHERE user_id={message.from_user.id}")
    if len(user) == 0:
        await insert_into_db(
            f"INSERT INTO stat(user_id, kol, koff, gets_kol, time, streak, activity) VALUES ({message.from_user.id}, 0, 0, 0, 0, 1, 0)")
        user = await select_from_db(
            f"SELECT kol, last, gets_kol, koff, time, bonus_date, promo FROM stat WHERE user_id={message.from_user.id}")

    kol: int = user[0]
    last: str | None = user[1]
    gets_kol: int = user[2] + 1
    koff_index: int = user[3]
    timezona: int = user[4]
    bonus_date: str | None = user[5]
    promo: str | None = user[6]

    """Преобразование текущего времени к часовому поясу пользователя"""
    dtime = await change_timedelta(datetime.datetime.now().strftime("%d.%m.%Y %X"), timezona)

    """Проверка на наличие промокода"""
    if not (promo is None):
        """Разделение на код и дату"""
        code_ = promo.split(';')
        code_, date = code_[0], code_[1]

        """Поиск кода"""
        val = await get_promo(code_)
        if not (val is None):
            if 'delta' in list(val.keys()):
                param = val['delta']

                """Окончание действия промокода"""
                if param[1] == 'days':
                    end = await change_timedelta(date + " 00:00:00", param[2] * 24)
                    end = end.split()[0]
                else:
                    end = param[2]

                if (await check_min_datetime(dtime, end + " 23:59:59")) == dtime:
                    DELTA = param[0]

    """Количество полученной валюты"""
    get_kol = koffs[koff_index]

    """Проверка на максимальный уровень (+2 - за 0-based индекс и за следующий уровень)"""
    if koff_index + 2 < len(koffs_kol):
        """Проверка на переход на новый уровень"""
        if gets_kol == koffs_kol[koff_index + 1]:
            lvl_up = True
            koff_index += 1

    """Проверка на соответствие времени"""
    if last is None:
        maybe = True

    else:
        """Бонус за новый день (не выдаётся при первом запуске)"""
        user_date = datetime.date.today().strftime("%d.%m.%Y %X")
        bonus = max(int(random.choice(chance) *
                        random.choice([7.5, 10, 12.5])), 1
                    ) * get_kol
        if bonus_date is None:
            have_bonus = True
        else:
            if (await check_min_datetime(user_date, bonus_date + " 00:00:00")) == bonus_date + " 00:00:00":
                have_bonus = True

            """Проверка на серию входов"""
            tomorrow = await change_timedelta(bonus_date + " 00:00:00", 24)
            if (await check_min_datetime(user_date, tomorrow)) == 0:
                streak = (await select_from_db(f"SELECT streak FROM stat WHERE user_id={message.from_user.id}"))[0] + 1
                await insert_into_db(f'UPDATE stat SET streak={streak} WHERE user_id={message.from_user.id}')
            else:
                streak = 0
                await insert_into_db(f'UPDATE stat SET streak=1 WHERE user_id={message.from_user.id}')

        if have_bonus:
            get_kol += bonus
            await insert_into_db(f'UPDATE stat SET bonus_date="{
            user_date.split()[0]}" WHERE user_id={message.from_user.id}')

        """Время следующего возможного получения валюты после времени из БД"""
        h2 = await change_timedelta(last, DELTA)

        """Сравнение текущего времени с временем получения"""
        if (await check_min_datetime(dtime, h2)) != dtime:
            maybe = True

    if maybe:
        """Обновление БД, ответ пользователю"""
        await insert_into_db(
            f'UPDATE stat SET kol={kol + get_kol + streak // 3}, last="{dtime}", koff={
            koff_index}, gets_kol={gets_kol} WHERE user_id={
            message.from_user.id}')

        if DELTA % 10 == 1 and DELTA // 10 != 1:
            add = ""
        elif DELTA % 10 in [2, 3, 4] and DELTA // 10 % 10 != 1:
            add = 'а'
        else:
            add = "ов"

        await message.reply(

            f'{message.from_user.full_name}, вы получили {get_kol + streak // 3}{param1[13]}\n'

            f'{"📦Ежедневный бонус: " + str(bonus) + param1[13] + "\n" if have_bonus else ""}'
            f'{"🔥Ежедневная серия: " + str(streak) + " (бонус: " + str(streak // 3) + param1[13] + ")\n" if streak > 1 else ""}'
            f'{"💥Ежедневная серия прервана!\n" if not streak else ""}'

            f'⏰Возвращайтесь через {DELTA} час{add}.\n'
            f'Всего: {kol + get_kol + streak // 3}{param1[13]}\n'

            f'{"🆙Новый уровень! " if lvl_up else ""}Ваш уровень: {
            koff_index + 1} (x{koffs[koff_index]}). \n{
            "До следующего уровня: " +
            str(koffs_kol[koff_index + 1] - gets_kol) if
            koff_index + 1 != len(koffs_kol) else ""}')

    else:
        dtime = await str_to_datetime(dtime)
        h2 = await str_to_datetime(h2)
        delta = h2 - dtime
        HH = delta.days * 24 + delta.seconds // 3600
        MM = delta.seconds // 60 - delta.seconds // 3600 * 60
        SS = delta.seconds - delta.seconds // 60 * 60
        await message.reply(f'Рано получать {param1[9]}!\n'
                            f'Возвращайтесь через {HH if HH else ""}{"ч" if HH else ""} {MM}мин {SS if not HH else ""}{"с" if not HH else ""}')


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
  

