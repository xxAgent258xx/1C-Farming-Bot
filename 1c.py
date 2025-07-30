import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
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
param1 = ["вуппит", "вуппита", "вуппиту", "вуппита", "вуппитом", "вуппите", "вуппиты", "вуппитов", "вуппитам", "вуппитов", "вуппитами", "вуппитах", "М", "🧸"]

"""Название персонажа во всех падежах, род/число в начальной форме ('М' / 'Ж' / 'СР' / 'МН'), эмодзи обычного и легендарного"""
param2 = ["вуппит", "вуппита", "вуппиту", "вуппита", "вуппитом", "вуппите", "вуппиты", "вуппитов", "вуппитам", "вуппитов", "вуппитами", "вуппитах", "М", "🧸", "🎠"]

"""Возможные разновидности легендарных персонажей"""
names = ["Лев", "Тигр", "Мышь", "Лошадь", "Пантера", "Кролик", "Капибара", "Волк", "Лисица", "Хомяк",
         "Утка", "Гусь", "Олень", "Бобёр", "Сова", "Медведь", "Панда", "Кенгуру", "Орёл", "Антилопа",
         "Енот", "Леопард", "Зебра", "Дракон", "Кошка"]

"""Названия характеристик в И.п., Р.п. и В.п. (ИИИРРРВВВ)"""
param3 = ["Шерсть", "Глаза", "Узор", "Шерсти", "Глаз", "Узора", "Шерсть", "Глаза", "Узор"]

"""Значения характеристик"""
values1 = ["Белая", "Рыжая", "Красная", "Голубая", "Жёлтая", "Малиновая", "Радужная", "Зелёная", "Фиолетовая", "Синяя"]
values2 = ["Белые", "Рыжие", "Красные", "Голубые", "Жёлтые", "Малиновые", "Радужные", "Зелёные", "Фиолетовые", "Синие"]
values3 = ["Полоска", "Клетка", "Пятна", "Цветы", "Камуфляж", "Леопард", "Звёзды", "Фигуры", "Сетка", "Рябь"]

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

chance = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
"""Коэффициенты"""
koffs = [1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
"""Количество использований, необходимое для применения коэффициента"""
koffs_kol = [0, 10, 50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
DB_NAME = '1c.db'
TOKEN = FARMING_BOT_TOKEN


"""Сравнивание дат для проверки на готовность получения валюты.
Даты хранятся в БД в виде строки в формате 01.01.2000 00:00:00.
Сравнение строк занимает O(1) времени, не влияет на асинхронность функций"""
def check_min_datetime(date1: str, date2: str):
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


"""Инициализация бота"""
bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


"""Стартовое сообщение с списком команд"""
@dp.message(CommandStart())
async def start(message: Message):

    await message.reply(
        f'Добро пожаловать в увлекательную игру!\nЗдесь ты сможешь получать {param1[9]} и обменивать их на легендарные!\n'
        '📋Список команд:\n'
        f'/get - получить {param1[3]}{param1[13]}\n'
        f'/buy - купить легендарн{add1} {param2[3]} за {price[0]}{param1[13]}\n'
        '/upgrade {№} {#} - прокачать ' + f'легендарн{add1} {param2[3]} за {price[1]}{param1[13]}\n'
        '/collect {№} - сделать полностью ' + f'прокачанн{add1} легендарн{add1} {param2[3]} коллекционн{add2} за {price[2]}{param1[13]}\n'
        '/name {№} {""} - задать имя ' + f'коллекционн{add3} {param2[2]}\n'
        '/me - посмотреть профиль\n'
        '/time {ЧЧ} - сменить разницу времени с МСК\n'
        '\n{№} - номер ' + f'{param2[1]}, с которым совершается действие\n'
        '{""} - имя ' + f'{param2[1]}\n'
        '{ЧЧ} - разница во времени от -15 до +11\n'
        '{#} - номер характеристики (1, 2 или 3)'

    )


"""Получение валюты"""
@dp.message(Command(commands=['get']))
async def get(message: Message):
    lvl_up = False
    value = 0
    new = True
    maybe = False
    bonus = 0

    """Подключение к БД"""
    async with aiosqlite.connect(DB_NAME) as db:
        """Проверка на наличие записи о пользователе"""
        async with db.execute(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                new = False
        if new:
            """Запись нового пользователя"""
            await db.execute(
                f'INSERT INTO stat(user_id, kol, koff, gets_kol, time) VALUES ({message.from_user.id}, 0, 0, 0, 0)')
            await db.commit()
            kol, last, koff_index, gets_kol, timezona, bonus_date = 0, None, 0, 0, 0, None
        else:
            """Получение значений из БД"""
            async with db.execute(
                    f'SELECT kol, last, gets_kol, koff, time, bonus_date FROM stat WHERE user_id={message.from_user.id}') as cursor:
                async for row in cursor:
                    kol = row[0]
                    last = row[1]
                    gets_kol = row[2] + 1
                    koff_index = row[3]
                    timezona = row[4]
                    bonus_date = row[5]

        """Преобразование текущего времени к часовому поясу пользователя"""
        if int(timezona) >= 0:
            dtime = (datetime.datetime.now() + datetime.timedelta(hours=int(timezona))).strftime("%d.%m.%Y %X")
        else:
            dtime = (datetime.datetime.now() - datetime.timedelta(hours=abs(int(timezona)))).strftime("%d.%m.%Y %X")

        """Количество полученной валюты"""
        get_kol = koffs[koff_index]

        if not (last is None):
            """Время следующего возможного получения валюты после времени из БД"""
            h2 = (datetime.datetime(day=int(last[0:2]), month=int(last[3:5]), year=int(last[6:10]),
                                    hour=int(last[11:13]), minute=int(last[14:16]),
                                    second=int(last[17:19])) + datetime.timedelta(hours=2)).strftime("%d.%m.%Y %X")

            """Бонус за новый день"""
            bonus = int(random.choice(chance) * 5 * random.choice([2, 2.5, 3])) * koffs[koff_index]
            if bonus_date is None:
                get_kol += bonus
                await db.execute(f'UPDATE stat SET bonus_date="{datetime.date.today().strftime("%d.%m.%Y")}" WHERE user_id={message.from_user.id}')
                await db.commit()
            else:
                if check_min_datetime(datetime.date.today().strftime("%d.%m.%Y %X"), bonus_date + " 00:00:00") == bonus_date + " 00:00:00":
                    get_kol += bonus
                    await db.execute(f'UPDATE stat SET bonus_date="{datetime.date.today().strftime("%d.%m.%Y")}" WHERE user_id={message.from_user.id}')
                    await db.commit()

        """Проверка на переход на новый уровень"""
        if koff_index + 1 < len(koffs_kol):
            if gets_kol == koffs_kol[koff_index + 1]:
                lvl_up = True
        """Проверка на соответствие времени"""
        if last is None:
            maybe = True
        elif check_min_datetime(dtime, h2) != dtime:
            maybe = True
        if maybe:
            """Обновление БД, ответ пользователю"""
            await db.execute(
                f'UPDATE stat SET kol={kol + get_kol}, last="{dtime}", koff={koff_index + (1 if lvl_up else 0)}, gets_kol={gets_kol} WHERE user_id={message.from_user.id}')
            await db.commit()
            await message.reply(
                f'{message.from_user.full_name}, вы получили {get_kol}{param1[13]}{" (Ежедневный бонус: " + str(bonus) + param1[13] + ")" if get_kol != koffs[koff_index] else ""}\n'
                f'Возвращайтесь через 2 часа. Всего: {kol + get_kol}{param1[13]}\n'
                f'{"Новый уровень! " if lvl_up else ""}Ваш уровень: {koff_index + 1 + (1 if lvl_up else 0)} (x{koffs[koff_index + (1 if lvl_up else 0)]}). {"До следующего уровня: " + str(koffs_kol[koff_index + 1 + (1 if lvl_up else 0)] - gets_kol) if koff_index + 1 != len(koffs_kol) else ""}')
        else:
            await message.reply(f'Рано получать {param1[9]}❌')


"""Покупка легендарного персонажа"""
@dp.message(Command(commands=['buy']))
async def buy(message: Message):
    balance = 0
    num = 1
    """Подключение к БД"""
    async with aiosqlite.connect(DB_NAME) as db:
        """Получение данных"""
        async with db.execute(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                balance = row[0]

        """ID легендарного персонажа уникален для пользователя, а не всей таблицы"""
        async with db.execute(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                if not (row[0] is None):
                    num = row[0] + 1
                else:
                    num = 1

        if balance >= price[0]:
            """Случайный выбор характеристик"""
            name_ = random.choice(names)
            value1 = random.choice(chance)
            value2 = random.choice(chance)
            value3 = random.choice(chance)

            """Запись в БД, ответ пользователю"""
            await db.execute(f'UPDATE stat SET kol={balance - price[0]} WHERE user_id={message.from_user.id}')
            await db.execute(
                f'INSERT INTO legendary(id, user_id, animal, value1, value2, value3) VALUES({num}, {message.from_user.id}, "{name_}", {value1}, {value2}, {value3})')
            await db.commit()
            await message.reply(f'Поздравляю с покупкой легендарн{add4} {param2[1]}!{param2[14]}\n'
                                f'№: {num}\n'
                                f'Вид: {name_}\n'
                                f'Уровень {param3[3]}: {value1}\n'
                                f'Уровень {param3[4]}: {value2}\n'
                                f'Уровень {param3[5]}: {value3}\n\n'
                                f'Прокачайте {param2[3]} до максимального уровня, чтобы сделать коллекционн{add2}!')
        else:
            await message.reply(f'Недостаточно {param1[7]}❌')


"""Профиль"""
@dp.message(Command(commands=['me']))
async def me(message: Message):
    text = ''
    prof = []
    count = 0
    """Подключение к БД"""
    async with aiosqlite.connect(DB_NAME) as db:
        """Получение значений, создание переменных"""
        async with db.execute(f'SELECT * FROM stat WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                prof = list(row)
                h2 = (datetime.datetime(day=int(prof[2][0:2]), month=int(prof[2][3:5]), year=int(prof[2][6:10]),
                                        hour=int(prof[2][11:13]), minute=int(prof[2][14:16]),
                                        second=int(prof[2][17:19])) + datetime.timedelta(hours=2)).strftime("%d.%m.%Y %X")
                if int(prof[5]) >= 0:
                    BOOL = check_min_datetime(h2, str((datetime.datetime.now() + datetime.timedelta(hours=int(prof[5]))).strftime("%d.%m.%Y %X"))) != h2
                else:
                    BOOL = check_min_datetime(h2, str((datetime.datetime.now() - datetime.timedelta(hours=abs(int(prof[5])))).strftime("%d.%m.%Y %X"))) != h2
        if not prof:
            """Запись нового пользователя"""
            await db.execute(
                f'INSERT INTO stat(user_id, kol, koff, gets_kol, time) VALUES ({message.from_user.id}, 0, 0, 0, 0)')
            await db.commit()
            prof = [message.from_user.id, 0, None, 0, 0, 0]
            BOOL = False

        """Получение информации о легендарных персонажах"""
        async with db.execute(f'SELECT * FROM legendary WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                count += 1
                text += f'№{row[0]}, {row[2]}{" " + row[3] if row[3] else ""}, {param3[0]}: {row[4] if row[4] else row[5]}, {param3[1]}: {row[6] if row[6] else row[7]}, {param3[2]}: {row[8] if row[8] else row[9]}\n'

    """Ответ пользователю"""
    await message.reply(f'🆔ID: {prof[0]}\n'
                        f'{param1[13]}{param1[7].capitalize()}: {prof[1]}\n'
                        f'{param1[13]}Всего получено: {prof[3]}\n'
                        f'↗️Ваш уровень: {prof[4] + 1} (x{koffs[prof[4]]})\n'
                        f'{"🆙До следующего уровня: " + str(koffs_kol[prof[4] + 1] - prof[3]) if prof[4] + 1 != len(koffs_kol) else ""}\n'
                        f'⏰Следующее получение: {h2 if BOOL else 'уже доступно! /get'}\n'
                        f'\n⚙️Часовой пояс: МСК{"+" if int(prof[5]) >= 0 else ""}{int(prof[5])}'
                        )
    if count > 0:
        await message.reply(f'{param2[14]}Легендарных {param2[7]}: {count}\n{text}')
    # print(prof)
    # print(text)


"""Прокачка легендарного персонажа"""
@dp.message(Command(commands=['upgrade']))
async def upgrade(message: Message):
    status = "OK"
    num = 0
    text = message.text.split()
    add = ''
    p1 = "0"
    p2 = "1"
    value = 0.0
    kol = 0

    if len(text) >= 3:
        p1 = text[1]
        p2 = text[2]
    else:
        status = "Недостаточно значений❌"

    """Подключение к БД"""
    async with aiosqlite.connect(DB_NAME) as db:
        """Получение информации о легендарных персонажах"""
        async with db.execute(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                if row is None:
                    status = f"Нет легендарных {param2[7]}❌"
                else:
                    num = row[0]

        """Проверка на корректность данных"""
        if p2 in ['1', '2', '3'] and p1 in [str(x) for x in range(1, num+1)]:
            """Получение уровня характеристики"""
            async with db.execute(
                    f'SELECT value{p2} FROM legendary WHERE user_id={message.from_user.id} AND id={p1}') as cursor:
                async for row in cursor:
                    if row is None:
                        status = "Неверные значения❌"
                    else:
                        value = row[0]
                        if value > 0.9:
                            status = "Достигнут максимальный уровень❌"
        else:
            status = "Неверные значения❌"
        """Получение баланса"""
        async with db.execute(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                if row is None:
                    status = f"Недостаточно {param1[7]}❌"
                else:
                    kol = row[0]
                    if kol < price[1]:
                        status = f"Недостаточно {param1[7]}❌"
        # if 1 <= int(text[2]) <= 3 and 1 <= int(text[1]) <= num and value <= 0.9 and kol >= 50:

        if status == "OK":
            """Запись в БД, ответ пользователю"""
            if text[2] == '1':
                add = param3[6]
            elif text[2] == '2':
                add = param3[7]
            else:
                add = param3[8]
            await db.execute(f'UPDATE stat SET kol={kol - price[1]} WHERE user_id={message.from_user.id}')
            await db.execute(
                f'UPDATE legendary SET value{text[2]} = {round(value + 0.1, 1)} WHERE user_id={message.from_user.id} AND id={text[1]}')
            await db.commit()
            await message.reply(f'Вы прокачали {add} до {round(value + 0.1, 1) if value < 0.9 else 1}!\n'
                                f'Ваш баланс: {kol - price[1]}{param1[13]}\n')
        else:
            await message.reply(status)


"""Сделать персонажа коллекционным"""
@dp.message(Command(commands=['collect', 'collectible', 'collected']))
async def collect(message: Message):
    status = "OK"
    enable_ = True
    num = 0
    kol = 0
    balance = 0
    check_values = 0
    text = message.text.split()
    if len(text) >= 2:
        num = text[1]
    else:
        status = "Недостаточно значений❌"
    """Подключение к БД"""
    async with aiosqlite.connect(DB_NAME) as db:
        """Проверка на свободные записи в БД"""
        async with db.execute('SELECT COUNT(*) FROM legendary') as cursor:
            async for row in cursor:
                if row is None:
                    enable_ = True
                else:
                    if len(names) * len(values1) * len(values2) * len(values3) == row[0]:
                        status = f"Коллекционные {param2[6]} закончились❌"

        """Получение информации из БД"""
        async with db.execute(
                f'SELECT value1, value2, value3 FROM legendary WHERE user_id={message.from_user.id} AND id={num}') as cursor:
            async for row in cursor:
                if row is None:
                    status = "Неверные значения❌"
                else:
                    check_values = sum(row)
                    if check_values < 3:
                        status = f"{param2[0].capitalize()} недостаточно прокачан❌"

        """Получение баланса"""
        async with db.execute(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                if row is None:
                    status = f"Недостаточно {param1[7]}❌"
                else:
                    balance = row[0]
                    if balance < price[2]:
                        status = f"Недостаточно {param1[7]}❌"

        if status == "OK":
            """Присвоение уникальных характеристик"""
            value1 = random.choice(values1)
            value2 = random.choice(values2)
            value3 = random.choice(values3)
            check = True
            """Первичная проверка, определение переменной"""
            async with db.execute(
                    f'SELECT id FROM legendary WHERE class1="{value1}" AND class2="{value2}" AND class3="{value3}"') as cursor:
                async for row in cursor:
                    if row is None:
                        check = True
                    else:
                        check = False

            """Запуск цикла на поиск доступных значений"""
            while not check:
                value1 = random.choice(values1)
                value2 = random.choice(values2)
                value3 = random.choice(values3)
                async with db.execute(
                        f'SELECT id FROM legendary WHERE class1="{value1}" AND class2="{value2}" AND class3="{value3}"') as cursor:
                    async for row in cursor:
                        if row is None:
                            check = True
                            break
                        else:
                            check = False

            """Запись в БД, ответ пользователю"""
            await db.execute(
                f'UPDATE legendary SET class1="{value1}", class2="{value2}", class3="{value3}" WHERE user_id={message.from_user.id} AND id={num}')
            await db.execute(f'UPDATE stat SET kol={balance - price[2]} WHERE user_id={message.from_user.id}')
            await db.commit()
            await message.reply(f'{param2[0].capitalize()} №{num} стал коллекционн{add2}!{param2[14]}\n'
                                f'{param3[0]}: {value1}\n'
                                f'{param3[1]}: {value2}\n'
                                f'{param3[2]}: {value3}\n'
                                f'Ваш баланс: {balance - price[2]}{param1[13]}')
        else:
            await message.reply(status)


@dp.message(Command(commands=['new_admin', 'add_admin']))
async def new_admin(message: Message):
    check = False
    id_ = 0
    if len(message.text.split()) >= 2:
        id_ = message.text.split()[1]
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(f'SELECT * FROM admins') as cursor:
            async for ADMIN_ID in cursor:
                if message.from_user.id == ADMIN_ID[0]:
                    check = True
                    break
        try:
            if check:
                await db.execute(f'INSERT INTO admins(id) VALUES({id_})')
                await db.commit()
                await message.reply('Админ добавлен!')
            else:
                await message.reply('Недостаточно прав❌')

        except:
            await message.reply('Неверный ID❌')


"""Присвоение имени легендарному персонажу"""
@dp.message(Command(commands=['name']))
async def naming(message: Message):
    if len(message.text.split()) >= 3:
        id_ = message.text.split()[1]
        name_ = ' '.join(message.text.split()[2:])
        count = 0
        """Подключение к БД"""
        async with aiosqlite.connect(DB_NAME) as db:
            """Получение значений"""
            async with db.execute(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}') as cursor:
                async for kol in cursor:
                    if not (kol[0] is None):
                        count = kol[0]
                    else:
                        count = 0
            try:
                """Проверка на наличие легендарных персонажей"""
                if count > 0:
                    if 1 <= int(id_) <= count:
                        """Проверка на возможную SQL-инъекцию"""
                        BOOL = '"' in name_ or "'" in name_ or ')' in name_ or '}' in name_ or '--' in name_ or '=' in name_ or \
                            'union' in name_.lower() or 'concat' in name_.lower() or '*' in name_ or ';' in name_ or '@' in name_ or \
                            '|' in name_ or '%' in name_ or '#' in name_ or 'select' in name_.lower() or 'where' in name_.lower() or \
                            '/' in name_ or 'delete' in name_.lower()
                        if not BOOL:
                            """Запись в БД, ответ пользователю"""
                            await db.execute(
                                f'UPDATE legendary SET name="{name_}" WHERE user_id={message.from_user.id} AND id={id_}')
                            await db.commit()
                            await message.reply('Имя изменено!')
                        else:
                            await message.reply('Недопустимые символы❌')
                            async with db.execute(f'SELECT * FROM admins') as cursor:
                                async for ADMIN_ID in cursor:
                                    await bot.send_message(ADMIN_ID[0], f'Попытка SQL-инъекции\nID: {message.from_user.id}\nТекст: {name_}')
                    else:
                        await message.reply('Неверный ID❌')
                else:
                    await message.reply(f'Нет легендарных {param2[7]}❌')
            except:
                await message.reply('Неверный ID❌')
    else:
        await message.reply('Недостаточно значений❌')


"""Смена часового пояса"""
@dp.message(Command(commands=['time', 'timezone', 'set_time']))
async def timezone(message: Message):
    if len(message.text.split()) >= 2:
        timer = message.text.split()[1]
        last = None
        old_time = 0
        new = True
        """Подключение к БД"""
        async with aiosqlite.connect(DB_NAME) as db:
            try:
                if -15 <= int(timer) <= 11:
                    """Получение значений"""
                    async with db.execute(f'SELECT last, time FROM stat WHERE user_id={message.from_user.id}') as cursor:
                        async for row in cursor:
                            last = row[0]
                            old_time = row[1]

                    """Смена часового пояса в записи в БД"""
                    if not (last is None):
                        if int(timer) - int(old_time) >= 0:
                            new_last = (datetime.datetime(day=int(last[0:2]), month=int(last[3:5]), year=int(last[6:10]),
                                                          hour=int(last[11:13]), minute=int(last[14:16]), second=int(last[17:19])
                                                          ) + datetime.timedelta(hours=int(timer) - int(old_time))).strftime("%d.%m.%Y %X")
                        else:
                            new_last = (datetime.datetime(day=int(last[0:2]), month=int(last[3:5]), year=int(last[6:10]),
                                                          hour=int(last[11:13]), minute=int(last[14:16]), second=int(last[17:19])
                                                          ) - datetime.timedelta(hours=int(old_time) - int(timer))).strftime(
                                "%d.%m.%Y %X")
                        await db.execute(
                            f'UPDATE stat SET last="{new_last}" WHERE user_id={message.from_user.id}')

                    """Проверка на нового пользователя"""
                    async with db.execute(f'SELECT time FROM stat WHERE user_id={message.from_user.id}') as cursor:
                        async for row in cursor:
                            new = False

                    """Запись в БД, ответ пользователю"""
                    if new:
                        await db.execute(
                            f'INSERT INTO stat(user_id, kol, koff, gets_kol, time) VALUES ({message.from_user.id}, 0, 0, 0, {int(timer)})')
                    else:
                        await db.execute(
                            f'UPDATE stat SET time={int(timer)} WHERE user_id={message.from_user.id}')
                    await db.commit()
                    await message.reply(f'Время изменено на МСК{"+" if int(timer) >= 0 else ""}{int(timer)}')
                else:
                    await message.reply('Неверное значение❌')

            except Exception:
                await message.reply('Неверное значение❌')
    else:
        await message.reply('Недостаточно значений❌')


# @dp.message(Command(commands=['promo', 'promocode', 'activate']))
# async def promo(message: Message):
#     code_ = ''
#     type_ = ''
#     block = ''
#     bonus = 0
#     balance = 0
#     text = message.text.split()
#     if len(text) >= 2:
#         code_ = text[1]
#         async with aiosqlite.connect(DB_NAME) as db:
#             async with db.execute(f'SELECT * FROM promo WHERE text={code_}') as cursor:
#                 async for row in cursor:
#                     if row is None:
#                         await message.reply('Неверный промокод❌')
#                     else:
#                         type_ = row[1]
#                         block = row[2]
#                         bonus = row[3]
#                         if type_ == 'kol':
#                             if block >= 1:
#                                 async with db.execute(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}') as cursor:
#                                     async for row in cursor:
#                                         if row is None:
#                                             balance = 0
#                                         else:
#                                             balance = row[0]
#     else:
#         await message.reply('Промокод не введён❌')


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
