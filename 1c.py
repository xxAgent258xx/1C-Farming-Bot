import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message
import aiosqlite
import datetime
import logging
import random

from tokens import FARMING_BOT_TOKEN

"""ПАРАМЕТРЫ ПРИЛОЖЕНИЯ"""
"""ПАРАМЕТРЫ ПРИЛОЖЕНИЯ"""
"""ПАРАМЕТРЫ ПРИЛОЖЕНИЯ"""

"""Название валюты во всех падежах, род/число в начальной форме ('М' / 'Ж' / 'СР' / 'МН'), эмодзи"""
param1 = ["вуппит", "вуппита", "вуппиту", "вуппита", "вуппитом", "вуппите",
          "вуппиты", "вуппитов", "вуппитам", "вуппитов", "вуппитами", "вуппитах",
          "М", "🧸"]

"""Название персонажа во всех падежах, род/число в начальной форме ('М' / 'Ж' / 'СР' / 'МН'), эмодзи обычного и легендарного"""
param2 = ["вуппит", "вуппита", "вуппиту", "вуппита", "вуппитом", "вуппите",
          "вуппиты", "вуппитов", "вуппитам", "вуппитов", "вуппитами", "вуппитах",
          "М", "🧸", "🎠"]

"""Возможные разновидности легендарных персонажей"""
names = ["Лев", "Тигр", "Мышь", "Лошадь", "Пантера",
         "Кролик", "Капибара", "Волк", "Лисица", "Хомяк",
         "Утка", "Гусь", "Олень", "Бобёр", "Сова",
         "Медведь", "Панда", "Кенгуру", "Орёл", "Антилопа",
         "Енот", "Леопард", "Зебра", "Дракон", "Кошка"]

"""Названия характеристик в И.п., Р.п. и В.п."""
param3 = ["Шерсть", "Глаза", "Узор",
          "Шерсти", "Глаз", "Узора",
          "Шерсть", "Глаза", "Узор"]

"""Значения характеристик"""
values1 = ["Белая", "Рыжая", "Красная", "Голубая", "Жёлтая",
           "Малиновая", "Радужная", "Зелёная", "Фиолетовая", "Синяя"]

values2 = ["Белые", "Рыжие", "Красные", "Голубые", "Жёлтые",
           "Малиновые", "Радужные", "Зелёные", "Фиолетовые", "Синие"]

values3 = ["Полоска", "Клетка", "Пятна", "Цветы", "Камуфляж",
           "Леопард", "Звёзды", "Фигуры", "Сетка", "Рябь"]

"""Стоимость покупки, прокачки легендарного персонажа, выпуска коллекционного"""
price = [50, 25, 30]

"""КОНЕЦ УСТАНОВКИ ПАРАМЕТРОВ"""
"""КОНЕЦ УСТАНОВКИ ПАРАМЕТРОВ"""
"""КОНЕЦ УСТАНОВКИ ПАРАМЕТРОВ"""

"""Окончания прилагательных для некоторых падежей"""
add1 = "ого" if param2[12] == 'М' else "ую" if param2[12] == 'Ж' else "ое" if param2[12] == 'СР' else 'ые'
add2 = "ой" if param2[12] == 'Ж' else "ыми" if param2[12] == 'МН' else "ым"
add3 = "ой" if param2[12] == 'Ж' else "ым" if param2[12] == 'МН' else "ому"
add4 = "ой" if param2[12] == 'Ж' else "ых" if param2[12] == 'МН' else "ого"
add5 = "ый" if param2[12] == 'М' else "ая" if param2[12] == 'Ж' else "ое" if param2[12] == 'СР' else 'ые'

chance = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

"""Коэффициенты"""
koffs = [1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
"""Количество использований, необходимое для применения коэффициента"""
koffs_kol = [0, 10, 50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000]

DB_NAME = '1c.db'
TOKEN = FARMING_BOT_TOKEN


async def check_min_datetime(date1: str, date2: str) -> str | int:
    if int(date1[6:11]) > int(date2[6:11]):
        return date2
    elif int(date1[6:11]) < int(date2[6:11]):
        return date1
    else:
        if int(date1[3:5]) > int(date2[3:5]):
            return date2
        elif int(date1[3:5]) < int(date2[3:5]):
            return date1
        else:
            if int(date1[0:2]) > int(date2[0:2]):
                return date2
            elif int(date1[0:2]) < int(date2[0:2]):
                return date1
            else:
                if int(date1[11:13]) > int(date2[11:13]):
                    return date2
                elif int(date1[11:13]) < int(date2[11:13]):
                    return date1
                else:
                    if int(date1[14:16]) > int(date2[14:16]):
                        return date2
                    elif int(date1[14:16]) < int(date2[14:16]):
                        return date1
                    else:
                        if int(date1[17:19]) > int(date2[17:19]):
                            return date2
                        elif int(date1[17:19]) < int(date2[17:19]):
                            return date1
                        else:
                            return 0


async def select_from_db(query: str) -> list:
    ans = []
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(query) as cursor:
            async for row in cursor:
                ans.append(list(row))
    if len(ans) == 1:
        return ans[0]
    else:
        return ans


async def change_timedelta(date: str, delta: int) -> str:
    if delta >= 0:
        ans = (datetime.datetime(day=int(date[0:2]),
                                 month=int(date[3:5]),
                                 year=int(date[6:10]),
                                 hour=int(date[11:13]),
                                 minute=int(date[14:16]),
                                 second=int(date[17:19]))
               + datetime.timedelta(hours=delta)).strftime("%d.%m.%Y %X")
    else:
        ans = (datetime.datetime(day=int(date[0:2]),
                                 month=int(date[3:5]),
                                 year=int(date[6:10]),
                                 hour=int(date[11:13]),
                                 minute=int(date[14:16]),
                                 second=int(date[17:19]))
               - datetime.timedelta(hours=abs(delta))).strftime("%d.%m.%Y %X")
    return ans


async def insert_into_db(query: str) -> None:
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(query)
        await db.commit()


async def get_promo(query: str) -> dict | None:
    # ans = {
    #     "balance": 0,
    #     "buy": 0,
    #     "delta": [2, "days", 0],
    #     "sale": 1
    #        }

    ans = {}
    promo = await select_from_db(f'SELECT bonus FROM promo WHERE text="{query}"')
    if len(promo) == 0:
        return None
    else:
        for i in [x.split(':') for x in promo[0].split(';')]:
            if i[0] == "delta":
                ans[i[0]] = i[1].split('_')
                """Смена типов данных"""
                ans[i[0]][0] = int(ans[i[0]][0])
                if ans[i[0]][1] == "days":
                    ans[i[0]][2] = int(ans[i[0]][2])
            elif i[0] == "sale":
                ans[i[0]] = i[1].split('_')
                """Смена типов данных"""
                ans[i[0]][0] = float(ans[i[0]][0])
                if ans[i[0]][1] == "days":
                    ans[i[0]][2] = int(ans[i[0]][2])
            else:
                ans[i[0]] = int(i[1])

        return ans


"""Инициализация бота"""
bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


"""Стартовое сообщение с списком команд"""
@dp.message(CommandStart())
async def start(message: Message, command: CommandObject) -> None:

    if command.args:
        """Проверка на наличие промокода"""
        if not ((await get_promo(command.args)) is None):
            await activate(message, promo=command.args)

    """Проверка на нового пользователя"""
    if len(await select_from_db(f'SELECT * FROM stat WHERE user_id={message.from_user.id}')) == 0:
        await insert_into_db(
            f"INSERT INTO stat(user_id, kol, koff, gets_kol, time) VALUES ({message.from_user.id}, 0, 0, 0, 0)")

    await message.reply(
        'Добро пожаловать в увлекательную игру!\n'
        f'Здесь ты сможешь получать {param1[9]} и обменивать их на легендарные!\n'
        '📋Список команд:\n'

        f'/get - получить {param1[3]}{param1[13]}\n'
        f'/buy - купить легендарн{add1} {param2[3]} за {price[0]}{param1[13]}\n'
        '/upgrade {№} {#} - прокачать ' +
        f'легендарн{add1} {param2[3]} за {price[1]}{param1[13]}\n'
        '/collect {№} - сделать полностью ' +
        f'прокачанн{add1} легендарн{add1} {param2[3]} коллекционн{add2} за {price[2]}{param1[13]}\n'
        '/name {№} {""} - задать имя ' + f'коллекционн{add3} {param2[2]}\n'
        '/me - посмотреть профиль\n'
        '/time {ЧЧ} - сменить разницу времени с МСК\n'

        '\n{№} - номер ' + f'{param2[1]}, с которым совершается действие\n'
        '{""} - имя ' + f'{param2[1]}\n'
        '{ЧЧ} - разница во времени от -15 до +11\n'
        '{#} - номер характеристики (1, 2 или 3)')


"""Получение валюты"""
@dp.message(Command(commands=['get']))
async def get(message: Message) -> None:
    lvl_up = False
    maybe = False
    have_bonus = False
    bonus = 0
    DELTA = 2

    """Получение значений из БД"""
    user = await select_from_db(
        f"SELECT kol, last, gets_kol, koff, time, bonus_date, promo FROM stat WHERE user_id={message.from_user.id}")
    kol: int = user[0]
    last: str | None = user[1]
    gets_kol: int = user[2] + 1
    koff_index: int = user[3]
    timezona: int = user[4]
    bonus_date: str | None = user[5]
    promo: str = user[6]

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
        user_date = await change_timedelta(datetime.date.today().strftime("%d.%m.%Y %X"), timezona)
        bonus = max(int(random.choice(chance) *
                        random.choice([7.5, 10, 12.5])), 1
                    ) * get_kol
        if bonus_date is None:
            have_bonus = True
        else:
            if (await check_min_datetime(user_date, bonus_date + " 00:00:00")) == bonus_date + " 00:00:00":
                have_bonus = True

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
            f'UPDATE stat SET kol={kol + get_kol}, last="{dtime}", koff={
            koff_index}, gets_kol={gets_kol} WHERE user_id={
            message.from_user.id}')

        if DELTA % 10 == 1 and DELTA // 10 != 1:
            add = ""
        elif DELTA % 10 in [2, 3, 4] and DELTA // 10 != 1:
            add = 'а'
        else:
            add = "ов"

        await message.reply(

            f'{message.from_user.full_name}, вы получили {get_kol}{param1[13]}{

            " (Ежедневный бонус: " + str(bonus) + param1[13] + ")" if have_bonus else ""}\n'

            f'Возвращайтесь через {DELTA} час{add}. Всего: {kol + get_kol}{param1[13]}\n'

            f'{"Новый уровень! " if lvl_up else ""}Ваш уровень: {
            koff_index + 1} (x{koffs[koff_index]}). {

            "До следующего уровня: " +
            str(koffs_kol[koff_index + 1] - gets_kol) if
            koff_index + 1 != len(koffs_kol) else ""}')

    else:
        await message.reply(f'Рано получать {param1[9]}❌')


"""Покупка легендарного персонажа"""
@dp.message(Command(commands=['buy']))
async def buy(message: Message, promo=0) -> None:
    koff = 1
    cursor = await select_from_db(f'SELECT kol, time, promo FROM stat WHERE user_id={message.from_user.id}')
    balance, timezona, PROMO = cursor[0], cursor[1], cursor[2]

    """Проверка на наличие промокода"""
    if not (PROMO is None):
        """Разделение на код и дату"""
        code_ = PROMO.split(';')
        code_, date = code_[0], code_[1]

        """Поиск кода"""
        val = await get_promo(code_)
        if not (val is None):
            if 'sale' in list(val.keys()):
                param = val['sale']

                """Преобразование текущего времени к часовому поясу пользователя"""
                dtime = await change_timedelta(datetime.datetime.now().strftime("%d.%m.%Y %X"), timezona)

                """Окончание действия промокода"""
                if param[1] == 'days':
                    end = await change_timedelta(date + " 00:00:00", param[2] * 24)
                    end = end.split()[0]
                else:
                    end = param[2]

                if (await check_min_datetime(dtime, end + " 23:59:59")) == dtime:
                    koff = param[0]

    """ID легендарного персонажа уникален для пользователя, а не всей таблицы"""
    num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
    if num is None:
        num = 1
    else:
        num += 1

    """Не выполняется, если не вызвано из промокода"""
    for i in range(promo):
        """Случайный выбор характеристик"""
        name_ = random.choice(names)
        value1 = random.choice(chance)
        value2 = random.choice(chance)
        value3 = random.choice(chance)

        """Запись в БД, ответ пользователю"""
        await insert_into_db(f'INSERT INTO legendary(id, user_id, animal, value1, value2, value3) VALUES({
        num}, {message.from_user.id}, "{name_}", {value1}, {value2}, {value3})')

        await message.reply(f'Вам выдан легендарн{add5} {param2[0]}!{param2[14]}\n'
                            f'№: {num}\n'
                            f'Вид: {name_}\n'
                            f'Уровень {param3[3]}: {value1}\n'
                            f'Уровень {param3[4]}: {value2}\n'
                            f'Уровень {param3[5]}: {value3}\n\n'
                            f'Прокачайте {param2[3]} до максимального уровня, чтобы сделать коллекционн{add2}!')

        num += 1

    if balance >= int(price[0] * koff) and not promo:
        """Случайный выбор характеристик"""
        name_ = random.choice(names)
        value1 = random.choice(chance)
        value2 = random.choice(chance)
        value3 = random.choice(chance)

        """Запись в БД, ответ пользователю"""
        await insert_into_db(f'UPDATE stat SET kol={balance - int(price[0] * koff)} WHERE user_id={message.from_user.id}')
        await insert_into_db(f'INSERT INTO legendary(id, user_id, animal, value1, value2, value3) VALUES({
        num}, {message.from_user.id}, "{name_}", {value1}, {value2}, {value3})')

        await message.reply(f'Поздравляю с покупкой легендарн{add4} {param2[1]}!{param2[14]}\n'
                            f'№: {num}\n'
                            f'Вид: {name_}\n'
                            f'Уровень {param3[3]}: {value1}\n'
                            f'Уровень {param3[4]}: {value2}\n'
                            f'Уровень {param3[5]}: {value3}\n\n'
                            f'Прокачайте {param2[3]} до максимального уровня, чтобы сделать коллекционн{add2}!')
    elif balance < int(price[0] * koff):
        await message.reply(f'Недостаточно {param1[7]}❌')


"""Профиль"""
@dp.message(Command(commands=['me']))
async def me(message: Message) -> None:
    text = ''
    count = 0

    """Получение профиля пользователя"""
    prof = await select_from_db(f'SELECT * FROM stat WHERE user_id={message.from_user.id}')
    h2 = await change_timedelta(prof[2], 2)

    """Преобразование текущего времени к часовому поясу пользователя"""
    dtime = await change_timedelta(datetime.datetime.now().strftime("%d.%m.%Y %X"), prof[5])

    BOOL = (await check_min_datetime(h2, dtime)) != h2

    """Получение информации о легендарных персонажах"""
    cursor = await select_from_db(f'SELECT * FROM legendary WHERE user_id={message.from_user.id}')
    for row in cursor:
        count += 1
        text += (f'№{row[0]}, {row[2]}{" " + row[3] if row[3] else ""}, '
                 f'{param3[0]}: {row[4] if row[4] else row[5]}, '
                 f'{param3[1]}: {row[6] if row[6] else row[7]}, '
                 f'{param3[2]}: {row[8] if row[8] else row[9]}\n')

    """Ответ пользователю"""
    await message.reply(f'🆔ID: {prof[0]}\n'
                        f'{param1[13]}{param1[7].capitalize()}: {prof[1]}\n'
                        f'{param1[13]}Всего получено: {prof[3]}\n'
                        f'↗️Ваш уровень: {prof[4] + 1} (x{koffs[prof[4]]})\n'
                        f'{"🆙До следующего уровня: " +
                           str(koffs_kol[prof[4] + 1] - prof[3]) if prof[4] + 1 != len(koffs_kol) else ""}\n'
                        f'⏰Следующее получение: {h2 if BOOL else 'уже доступно! /get'}\n'
                        f'\n⚙️Часовой пояс: МСК{"+" if prof[5] >= 0 else ""}{prof[5]}'
                        )
    if count > 0:
        await message.reply(f'{param2[14]}Легендарных {param2[7]}: {count}\n{text}')


"""Прокачка легендарного персонажа"""
@dp.message(Command(commands=['upgrade']))
async def upgrade(message: Message) -> None:
    status = "OK"
    num = 0
    text = message.text.split()
    add = ''
    p1 = "0"
    p2 = "1"
    value = 0.0

    koff = 1
    cursor = await select_from_db(f'SELECT kol, time, promo FROM stat WHERE user_id={message.from_user.id}')
    kol, timezona, PROMO = cursor[0], cursor[1], cursor[2]

    """Проверка на наличие промокода"""
    if not (PROMO is None):
        """Разделение на код и дату"""
        code_ = PROMO.split(';')
        code_, date = code_[0], code_[1]

        """Поиск кода"""
        val = await get_promo(code_)
        if not (val is None):
            if 'sale' in list(val.keys()):
                param = val['sale']

                """Преобразование текущего времени к часовому поясу пользователя"""
                dtime = await change_timedelta(datetime.datetime.now().strftime("%d.%m.%Y %X"), timezona)

                """Окончание действия промокода"""
                if param[1] == 'days':
                    end = await change_timedelta(date + " 00:00:00", param[2] * 24)
                    end = end.split()[0]
                else:
                    end = param[2]

                if (await check_min_datetime(dtime, end + " 23:59:59")) == dtime:
                    koff = param[0]

    if len(text) >= 3:
        p1 = text[1]
        p2 = text[2]
    else:
        status = "Недостаточно значений❌"

    """Проверка количества легендарных персонажей"""
    cursor = await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}')
    if cursor[0] is None:
        status = f"Нет легендарных {param2[7]}❌"
    else:
        num = cursor[0]

    """Проверка на корректность данных"""
    if p2 in ['1', '2', '3'] and p1 in [str(x) for x in range(1, num + 1)]:
        """Получение уровня характеристики"""
        value = (await select_from_db(
            f'SELECT value{p2} FROM legendary WHERE user_id={message.from_user.id} AND id={p1}'))[0]
        if value > 0.9:
            status = "Достигнут максимальный уровень❌"
    else:
        status = "Неверные значения❌"

    """Получение баланса"""
    if kol < int(price[1] * koff):
        status = f"Недостаточно {param1[7]}❌"

    if status == "OK":
        """Запись в БД, ответ пользователю"""
        add = param3[5 + int(p2)]

        await insert_into_db(f'UPDATE stat SET kol={kol - int(price[1] * koff)} WHERE user_id={message.from_user.id}')
        await insert_into_db(
            f'UPDATE legendary SET value{p2} = {round(value + 0.1, 1)} WHERE user_id={message.from_user.id} AND id={text[1]}')

        await message.reply(f'Вы прокачали {add} до {round(value + 0.1, 1)}!\n'
                            f'Ваш баланс: {kol - int(price[1] * koff)}{param1[13]}\n')
    else:
        await message.reply(status)


"""Сделать персонажа коллекционным"""
@dp.message(Command(commands=['collect', 'collectible', 'collected']))
async def collect(message: Message) -> None:
    status = "OK"
    koff = 1

    cursor = await select_from_db(f'SELECT kol, time, promo FROM stat WHERE user_id={message.from_user.id}')
    balance, timezona, PROMO = cursor[0], cursor[1], cursor[2]

    """Проверка на наличие промокода"""
    if not (PROMO is None):
        """Разделение на код и дату"""
        code_ = PROMO.split(';')
        code_, date = code_[0], code_[1]

        """Поиск кода"""
        val = await get_promo(code_)
        if not (val is None):
            if 'sale' in list(val.keys()):
                param = val['sale']

                """Преобразование текущего времени к часовому поясу пользователя"""
                dtime = await change_timedelta(datetime.datetime.now().strftime("%d.%m.%Y %X"), timezona)

                """Окончание действия промокода"""
                if param[1] == 'days':
                    end = await change_timedelta(date + " 00:00:00", param[2] * 24)
                    end = end.split()[0]
                else:
                    end = param[2]

                if (await check_min_datetime(dtime, end + " 23:59:59")) == dtime:
                    koff = param[0]

    text = message.text.split()
    if len(text) >= 2:
        try:
            num = int(text[1])
        except ValueError:
            num = 0
    else:
        num = 0
        status = "Недостаточно значений❌"

    """Проверка на свободные записи в БД"""
    cursor = (await select_from_db('SELECT COUNT(*) FROM legendary'))[0]
    if len(names) * len(values1) * len(values2) * len(values3) == cursor:
        status = f"Коллекционные {param2[6]} закончились❌"

    """Получение допустимых значений"""
    count = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
    if count is None:
        count = 0

    if 1 <= num <= count:
        """Получение информации из БД"""
        cursor = await select_from_db(
            f'SELECT value1, value2, value3 FROM legendary WHERE user_id={message.from_user.id} AND id={int(num)}')
        if len(cursor) == 0:
            status = "Неверные значения❌"
        else:
            check_values = sum(cursor)
            if check_values < 3:
                status = f"{param2[0].capitalize()} недостаточно прокачан❌"
    else:
        status = "Неверные значения❌"

    """Получение баланса"""
    balance = (await select_from_db(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}'))[0]
    if balance < int(price[2] * koff):
        status = f"Недостаточно {param1[7]}❌"

    if status == "OK":
        """Присвоение уникальных характеристик"""
        value1 = random.choice(values1)
        value2 = random.choice(values2)
        value3 = random.choice(values3)

        """Первичная проверка, определение переменной"""
        cursor = await select_from_db(
            f'SELECT id FROM legendary WHERE class1="{value1}" AND class2="{value2}" AND class3="{value3}"')

        """Запуск цикла на поиск доступных значений"""
        while len(cursor) != 0:
            value1 = random.choice(values1)
            value2 = random.choice(values2)
            value3 = random.choice(values3)
            cursor = await select_from_db(
                f'SELECT id FROM legendary WHERE class1="{value1}" AND class2="{value2}" AND class3="{value3}"')

        """Запись в БД, ответ пользователю"""
        await insert_into_db(
            f'UPDATE legendary SET class1="{value1}", class2="{value2}", class3="{value3}" WHERE user_id={message.from_user.id} AND id={int(num)}')
        await insert_into_db(f'UPDATE stat SET kol={balance - int(price[2] * koff)} WHERE user_id={message.from_user.id}')
        await message.reply(f'{param2[0].capitalize()} №{num} стал коллекционн{add2}!{param2[14]}\n'
                            f'{param3[0]}: {value1}\n'
                            f'{param3[1]}: {value2}\n'
                            f'{param3[2]}: {value3}\n'
                            f'Ваш баланс: {balance - int(price[2] * koff)}{param1[13]}')
    else:
        await message.reply(status)


@dp.message(Command(commands=['new_admin', 'add_admin']))
async def new_admin(message: Message) -> None:
    check = False
    id_ = 0
    if len(message.text.split()) >= 2:
        id_ = message.text.split()[1]
    cursor = await select_from_db(f'SELECT * FROM admins WHERE id={message.from_user.id}')
    if len(cursor) > 0:
        check = True

    try:
        if check:
            await insert_into_db(f'INSERT INTO admins(id) VALUES({int(id_)})')
            await message.reply('Админ добавлен!')
        else:
            await message.reply('Недостаточно прав❌')

    except ValueError:
        await message.reply('Неверный ID❌')


"""Присвоение имени легендарному персонажу"""
@dp.message(Command(commands=['name']))
async def naming(message: Message) -> None:
    if len(message.text.split()) >= 3:
        id_ = message.text.split()[1]
        name_ = ' '.join(message.text.split()[2:])

        count = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
        if count is None:
            count = 0
        try:
            """Проверка на наличие легендарных персонажей"""
            if count > 0:
                if 1 <= int(id_) <= count:
                    """Проверка на возможную SQL-инъекцию"""
                    BOOL = '"' in name_ or "'" in name_ or ')' in name_ or \
                            ']' in name_ or '}' in name_ or '--' in name_ or \
                            '=' in name_ or 'union' in name_.lower() or \
                            'concat' in name_.lower() or '*' in name_ or \
                            ';' in name_ or '@' in name_ or '|' in name_ or \
                            (r'\ '[0]) in name_ or '%' in name_ or \
                            '#' in name_ or '&' in name_ or '$' in name_ or \
                            'select' in name_.lower() or 'where' in name_.lower() or \
                            '/' in name_ or 'delete' in name_.lower()
                    if not BOOL:
                        """Запись в БД, ответ пользователю"""
                        await insert_into_db(
                                f'UPDATE legendary SET name="{name_}" WHERE user_id={message.from_user.id} AND id={id_}')
                        await message.reply('Имя изменено!')
                    else:
                        await message.reply('Недопустимые символы❌')
                        cursor = await select_from_db(f'SELECT * FROM admins')
                        for ADMIN in cursor:
                            await bot.send_message(ADMIN[0],
                                                   f'Попытка SQL-инъекции\nID: {message.from_user.id}\nТекст: {name_}')
                else:
                    await message.reply('Неверный ID❌')
            else:
                await message.reply(f'Нет легендарных {param2[7]}❌')
        except ValueError:
            await message.reply('Неверный ID❌')
    else:
        await message.reply('Недостаточно значений❌')


"""Смена часового пояса"""
@dp.message(Command(commands=['time', 'timezone', 'set_time']))
async def timezone(message: Message) -> None:
    if len(message.text.split()) >= 2:
        timer = message.text.split()[1]

        try:
            if -15 <= int(timer) <= 11:
                timer = int(timer)
                """Получение значений"""
                cursor = await select_from_db(
                    f'SELECT last, time FROM stat WHERE user_id={message.from_user.id}')
                last = cursor[0]
                old_time = cursor[1]

                """Смена часового пояса в записи в БД"""
                if not (last is None):
                    new_last = await change_timedelta(last, timer - old_time)

                    """Запись в БД, ответ пользователю"""
                    await insert_into_db(
                        f'UPDATE stat SET last="{new_last}" WHERE user_id={message.from_user.id}')

                    await insert_into_db(
                        f'UPDATE stat SET time={timer} WHERE user_id={message.from_user.id}')

                    await message.reply(f'Время изменено на МСК{"+" if timer >= 0 else ""}{timer}')
                else:
                    await message.reply('Неверное значение❌')

        except ValueError:
            await message.reply('Неверное значение❌')
    else:
        await message.reply('Недостаточно значений❌')


@dp.message(Command(commands=['promo', 'promocode', 'activate']))
async def activate(message: Message, promo="") -> None:
    bonus = False

    """Проверка, отсутствует ли активированный промокод"""
    if (await select_from_db(f"SELECT promo FROM stat WHERE user_id={message.from_user.id}"))[0] is None:
        """Проверка, был ли передан промокод"""
        if promo == "":
            text = message.text.split()
            if len(text) >= 2:
                promo = text[1]
                if not ((await get_promo(promo)) is None):
                    bonus = await get_promo(promo)
                else:
                    await message.reply("Промокод не найден❌")
            else:
                await message.reply("Промокод не введён❌")
        else:
            bonus = await get_promo(promo)

        if bonus:
            """Преобразование текущего времени к часовому поясу пользователя"""
            timezona = (await select_from_db(f"SELECT time FROM stat WHERE user_id={message.from_user.id}"))[0]
            dtime = await change_timedelta(datetime.datetime.now().strftime("%d.%m.%Y %X"), timezona)

            """Отделение даты"""
            dtime = dtime.split()[0]

            """Запись промокода и даты активации"""
            await insert_into_db(f'UPDATE stat SET promo="{promo};{dtime}" WHERE user_id={message.from_user.id}')

            """Выдача вознаграждений"""
            keys = list(bonus.keys())
            if "balance" in keys:
                kol = await select_from_db(f"SELECT kol FROM stat WHERE user_id={message.from_user.id}")
                await insert_into_db(f"UPDATE stat SET kol={kol[0] + bonus["balance"]} WHERE user_id={message.from_user.id}")
                await message.reply(f"Зачислено {kol}{param1[13]}")
            if "buy" in keys:
                await buy(message, promo=bonus["buy"])

    else:
        await message.reply("Вы уже активировали промокод❌")


async def on_startup():
    bot_info = await bot.get_me()
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(f'SELECT * FROM admins') as cursor:
            async for ADMIN in cursor:
                await bot.send_message(ADMIN[0], f'Бот @{bot_info.username} включён')


async def on_shutdown():
    bot_info = await bot.get_me()
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(f'SELECT * FROM admins') as cursor:
            async for ADMIN in cursor:
                await bot.send_message(ADMIN[0], f'Бот @{bot_info.username} выключен')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
