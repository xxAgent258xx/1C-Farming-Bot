import random
import datetime
import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import InlineQueryResultType
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ReplyKeyboardRemove, InlineQuery, ReplyKeyboardMarkup, KeyboardButton, \
    InlineQueryResultArticle, InputTextMessageContent
from aiogram.fsm.context import FSMContext

from tokens import FARMING_BOT_TOKEN

"""ПАРАМЕТРЫ ПРИЛОЖЕНИЯ"""
"""ПАРАМЕТРЫ ПРИЛОЖЕНИЯ"""
"""ПАРАМЕТРЫ ПРИЛОЖЕНИЯ"""

"""Название валюты во всех падежах, род/число в начальной форме ('М' / 'Ж' / 'СР' / 'МН'), эмодзи"""
param1 = ["вуппкоин", "вуппкоина", "вуппкоину", "вуппкоин", "вуппкоином", "вуппкоине",
          "вуппкоины", "вуппкоинов", "вуппкоинам", "вуппкоины", "вуппкоинами", "вуппкоинах",
          "М", "🧸"]

"""Название персонажа во всех падежах, род/число в начальной форме ('М' / 'Ж' / 'СР' / 'МН'), эмодзи обычного и коллекционного"""
param2 = ["вуппит", "вуппита", "вуппиту", "вуппита", "вуппитом", "вуппите",
          "вуппиты", "вуппитов", "вуппитам", "вуппитов", "вуппитами", "вуппитах",
          "М", "🧸", "🎠"]

"""Возможные разновидности легендарных персонажей"""
names = ["Лев", "Тигр", "Мышь", "Лошадь", "Цыплёнок",
         "Кролик", "Единорог", "Волк", "Лисица", "Хомяк",
         "Утка", "Гусь", "Олень", "Бобёр", "Сова",
         "Медведь", "Панда", "Кенгуру", "Орёл", "Лебедь",
         "Енот", "Леопард", "Зебра", "Дракон", "Кошка"]

emoji = {
    "Лев": "https://emojigraph.org/media/apple/lion_1f981.png",
    "Тигр": "https://emojigraph.org/media/whatsapp/tiger-face_1f42f.png",
    "Мышь": "https://emojigraph.org/media/whatsapp/mouse-face_1f42d.png",
    "Лошадь": "https://emojigraph.org/media/facebook/horse-face_1f434.png",
    "Цыплёнок": "https://emojigraph.org/media/facebook/hatching-chick_1f423.png",
    "Кролик": "https://emojigraph.org/media/apple/rabbit-face_1f430.png",
    "Единорог": "https://emojigraph.org/media/facebook/unicorn_1f984.png",
    "Волк": "https://emojigraph.org/media/facebook/wolf_1f43a.png",
    "Лисица": "https://emojigraph.org/media/whatsapp/fox_1f98a.png",
    "Хомяк": "https://emojigraph.org/media/apple/hamster_1f439.png",
    "Утка": "https://emojigraph.org/media/whatsapp/duck_1f986.png",
    "Гусь": "https://emojigraph.org/media/apple/goose_1fabf.png",
    "Олень": "https://emojigraph.org/media/facebook/deer_1f98c.png",
    "Бобёр": "https://emojigraph.org/media/apple/beaver_1f9ab.png",
    "Сова": "https://emojigraph.org/media/apple/owl_1f989.png",
    "Медведь": "https://emojigraph.org/media/whatsapp/bear_1f43b.png",
    "Панда": "https://emojigraph.org/media/whatsapp/panda_1f43c.png",
    "Кенгуру": "https://emojigraph.org/media/facebook/kangaroo_1f998.png",
    "Орёл": "https://emojigraph.org/media/apple/eagle_1f985.png",
    "Лебедь": "https://emojigraph.org/media/facebook/swan_1f9a2.png",
    "Енот": "https://emojigraph.org/media/facebook/raccoon_1f99d.png",
    "Леопард": "https://emojigraph.org/media/facebook/leopard_1f406.png",
    "Зебра": "https://emojigraph.org/media/facebook/zebra_1f993.png",
    "Дракон": "https://emojigraph.org/media/whatsapp/dragon-face_1f432.png",
    "Кошка": "https://emojigraph.org/media/facebook/cat-face_1f431.png"
}

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

"""Инициализация бота"""
storage = MemoryStorage()
bot = Bot(token=FARMING_BOT_TOKEN)
dp = Dispatcher(storage=storage)
DB_NAME = '/data/1c.db'

"""Меню бота"""
main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='▶️ Старт'), KeyboardButton(text='⬇️ Свернуть меню')],
    [KeyboardButton(text=f'{param1[13]} Получить {param1[9]}'),
     KeyboardButton(text=f'{param2[13]} Купить {param2[3]}')],
    [KeyboardButton(text=f'{param2[13]} Улучшить {param2[3]}'), KeyboardButton(text=f'{param2[13]} Имя {param2[1]}')],
    [KeyboardButton(text=f'{param2[14]} Коллекционный {param2[0]}'), KeyboardButton(text='👤 Профиль')],
    [KeyboardButton(text='📋 Список команд'), KeyboardButton(text='⚙️ Часовой пояс')]
], resize_keyboard=True)

# main_keyboard.keyboard[0][0].text
time_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='◀️ Отмена')],
    [KeyboardButton(text='UTC+2 (МСК-1)'), KeyboardButton(text='UTC+3 (МСК)')],
    [KeyboardButton(text='UTC+4 (МСК+1)'), KeyboardButton(text='UTC+5 (МСК+2)')],
    [KeyboardButton(text='UTC+6 (МСК+3)'), KeyboardButton(text='UTC+7 (МСК+4)')],
    [KeyboardButton(text='UTC+8 (МСК+5)'), KeyboardButton(text='UTC+9 (МСК+6)')],
    [KeyboardButton(text='UTC+10 (МСК+7)'), KeyboardButton(text='UTC+11 (МСК+8)')]
], resize_keyboard=True)

cancel_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='◀️ Отмена')]], resize_keyboard=True)


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


async def str_to_datetime(date: str) -> datetime.datetime:
    ans = datetime.datetime(day=int(date[0:2]),
                            month=int(date[3:5]),
                            year=int(date[6:10]),
                            hour=int(date[11:13]),
                            minute=int(date[14:16]),
                            second=int(date[17:19]))
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


class Form1(StatesGroup):
    value = State()


class Form2(StatesGroup):
    value = State()
    name = State()


class Form3(StatesGroup):
    value = State()


class Form4(StatesGroup):
    value = State()


class Form5(StatesGroup):
    value = State()
    cost = State()


class Form6(StatesGroup):
    value = State()


START_TEXT = \
    'Добро пожаловать в увлекательную игру!\n' + \
    f'Здесь ты сможешь получать {param1[9]}, покупать легендарные {param2[6]}, прокачивать их и делать коллекционными!\n' + \
    f'Список команд: /menu'

CMD_TEXT =\
    '📋Список команд:\n' + \
    f'/get - получить {param1[3]}{param1[13]}\n' + \
    f'/buy - купить легендарн{add1} {param2[3]} за {price[0]} {param1[7]}{param1[13]}\n' + \
    '/upgrade - прокачать ' + \
    f'легендарн{add1} {param2[3]} за {price[1]} {param1[7]}{param1[13]}\n' + \
    '/collect - сделать ' + \
    f'легендарн{add1} {param2[3]} коллекционн{add2} за {price[2]} {param1[7]}{param1[13]}\n' + \
    '/sell - выставить на продажу ' + f'коллекционн{add1} {param2[3]}\n' + \
    '@wuppit_bot 🔤 🔤 🔤 - открыть Маркет (для пропуска фильтра любой символ)\n' + \
    '/market 🔤 🔤 🔤 - приобрести ' + f'коллекционн{add1} {param2[3]}\n' + \
    '/name - задать имя ' + f'{param2[2]}\n' + \
    '/me - посмотреть профиль\n' + \
    '/promo - активировать промокод\n' + \
    '/time - сменить разницу времени с МСК\n' + \
    '\nПараметры:\n' + \
    '🔤 - значение характеристики (слово)\n'

logging.basicConfig(level=logging.INFO)


@dp.message(F.text == cancel_keyboard.keyboard[0][0].text)
async def cancel(message: Message, state: FSMContext):
    await message.reply("Действие отменено. Список команд: /menu", reply_markup=main_keyboard)
    await state.clear()


"""Прокачка легендарного персонажа"""


async def upgrade_main(message: Message, p1="", p2="") -> None:
    status = "OK"
    num = 0
    text = message.text.split()
    value = 0.0
    koff = 1
    cursor = await select_from_db(f'SELECT kol, time, promo FROM stat WHERE user_id={message.from_user.id}')
    try:
        kol, timezona, PROMO = cursor[0], cursor[1], cursor[2]
    except IndexError:
        kol, timezona, PROMO = 0, 0, None

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

    if not (p1 and p2):
        if len(text) >= 3:
            p1 = text[1]
            p2 = text[2]
        else:
            status = ("Недостаточно значений❌\n"
                      "Пример команды: /upgrade 1 1")

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
        status = ("Неверные значения❌\n"
                  "Пример команды: /upgrade 1 1")

    """Получение баланса"""
    if kol // int(price[1] * koff) == 0:
        status = f"Недостаточно {param1[7]}❌"
    if status == "OK":
        """Запись в БД, ответ пользователю"""
        add = param3[5 + int(p2)]

        lvls = min(kol // int(price[1] * koff), (1 - value) * 10)
        new_kol = round(kol - lvls * int(price[1] * koff), 0)
        new_value = round(value + 0.1 * lvls, 1)

        await insert_into_db(f'UPDATE stat SET kol={new_kol} WHERE user_id={message.from_user.id}')
        await insert_into_db(
            f'UPDATE legendary SET value{p2} = {new_value} WHERE user_id={message.from_user.id} AND id={p1}')

        await message.reply(f'Вы прокачали {add} до {new_value}!\n'
                            f'Ваш баланс: {new_kol}{param1[13]}\n', reply_markup=main_keyboard)
    else:
        await message.reply(status, reply_markup=main_keyboard)


"""Сделать персонажа коллекционным"""


@dp.message(Command(commands=['collect', 'collectible', 'collected']))
async def collect_main(message: Message, num_="") -> None:
    status = "OK"
    koff = 1

    cursor = await select_from_db(f'SELECT kol, time, promo FROM stat WHERE user_id={message.from_user.id}')
    try:
        balance, timezona, PROMO = cursor[0], cursor[1], cursor[2]
    except IndexError:
        balance, timezona, PROMO = 0, 0, None

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
    if not num_:
        if len(text) >= 2:
            try:
                num = int(text[1])
            except ValueError:
                num = 0
        else:
            num = 0
            status = ("Недостаточно значений❌\n"
                      "Пример команды: /collect 1")
    else:
        try:
            num = int(num_)
        except ValueError:
            num = 0

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
            f'SELECT class1, value1, value2, value3 FROM legendary WHERE user_id={message.from_user.id} AND id={int(num)}')
        if len(cursor) == 0:
            status = ("Неверные значения❌\n"
                      "Пример команды: /collect 1")
        else:
            check_values = sum(cursor[1:])
            if check_values < 3:
                status = f"{param2[0].capitalize()} недостаточно прокачан❌"

            if not (cursor[0] is None):
                status = f"{param2[0].capitalize()} уже коллекционный❌"
    else:
        status = ("Неверные значения❌\n"
                  "Пример команды: /collect 1")

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
        await insert_into_db(
            f'UPDATE stat SET kol={balance - int(price[2] * koff)} WHERE user_id={message.from_user.id}')
        await message.reply(f'{param2[0].capitalize()} №{num} стал коллекционн{add2}!{param2[14]}\n'
                            f'{param3[0]}: {value1}\n'
                            f'{param3[1]}: {value2}\n'
                            f'{param3[2]}: {value3}\n'
                            f'Ваш баланс: {balance - int(price[2] * koff)}{param1[13]}',
                            reply_markup=main_keyboard)
    else:
        await message.reply(status, reply_markup=main_keyboard)


"""Присвоение имени легендарному персонажу"""


async def naming_main(message: Message, id_="", name_="") -> None:
    if len(message.text.split()) >= 3 or name_:
        if not name_:
            id_ = message.text.split()[1]
            name_ = ' '.join(message.text.split()[2:])

        count = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
        if count is None:
            count = 0
        try:
            """Проверка на наличие легендарных персонажей"""
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
                    if len(name_) <= 25:
                        """Запись в БД, ответ пользователю"""
                        await insert_into_db(
                                f'UPDATE legendary SET name="{name_}" WHERE id={id_} AND user_id={message.from_user.id}')
                        await message.reply('Имя изменено!',
                                            reply_markup=main_keyboard)
                    else:
                        await message.reply('Слишком длинное имя❌', reply_markup=main_keyboard)
                else:
                    await message.reply('Недопустимые символы❌',
                                        reply_markup=main_keyboard)
                    cursor = await select_from_db(f'SELECT * FROM admins')
                    for ADMIN in cursor:
                        if ADMIN[2]:
                            await bot.send_message(ADMIN[0],
                                                   f'Попытка SQL-инъекции\nID: {message.from_user.id}\nТекст: {name_}')
            else:
                await message.reply(f'Неверный номер {param2[1]}❌',
                                    reply_markup=main_keyboard)
        except ValueError:
            await message.reply(f'Неверный номер {param2[1]}❌',
                                reply_markup=main_keyboard)
    else:
        await message.reply('Недостаточно значений❌\n'
                            'Пример команды: /name 1 Имя',
                            reply_markup=main_keyboard)


"""Смена часового пояса"""


async def timezone_main(message: Message, timer="") -> None:
    if len(message.text.split()) >= 2 or timer:
        if not timer:
            timer = message.text.split()[1]

        try:
            if -15 <= int(timer) <= 11:
                timer = int(timer)
                """Получение значений"""
                cursor = await select_from_db(
                    f'SELECT last, time FROM stat WHERE user_id={message.from_user.id}')

                try:
                    last = cursor[0]
                    old_time = cursor[1]
                    await insert_into_db(
                        f'UPDATE stat SET time={timer} WHERE user_id={message.from_user.id}')

                    """Смена часового пояса в записи в БД"""
                    if not (last is None):
                        new_last = await change_timedelta(last, timer - old_time)
                        """Запись в БД, ответ пользователю"""
                        await insert_into_db(
                            f'UPDATE stat SET last="{new_last}" WHERE user_id={message.from_user.id}')

                except IndexError:
                    await insert_into_db(
                        f"INSERT INTO stat(user_id, kol, koff, gets_kol, time, streak, activity) VALUES ({message.from_user.id}, 0, 0, 0, {timer}, 1, 0)")

                await message.reply(f'Время изменено на МСК{"+" if timer >= 0 else ""}{timer}',
                                    reply_markup=main_keyboard)
            else:
                await message.reply('Неверное значение❌\n'
                                    'Пример команды: /time +1',
                                    reply_markup=main_keyboard)
        except ValueError:
            await message.reply('Неверное значение❌\n'
                                'Пример команды: /time +1',
                                reply_markup=main_keyboard)
    else:
        await message.reply('Недостаточно значений❌\n'
                            'Пример команды: /time +1',
                            reply_markup=main_keyboard)


"""Активация промокода"""


async def activate_main(message: Message, promo="") -> None:
    bonus = False
    PROMO = await select_from_db(f"SELECT promo FROM stat WHERE user_id={message.from_user.id}")
    if len(PROMO) == 0:
        await insert_into_db(
            f"INSERT INTO stat(user_id, kol, koff, gets_kol, time, streak, activity) VALUES ({message.from_user.id}, 0, 0, 0, 0, 1, 0)")
    """Проверка, отсутствует ли активированный промокод"""
    if PROMO[0] is None:
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
                await message.reply(f"Зачислено {bonus["balance"]}{param1[13]}")
            if "buy" in keys:
                await buy_main(message, promo=bonus["buy"])
        else:
            await message.reply("Промокод не найден❌")
    else:
        await message.reply("Вы уже активировали промокод❌")


@dp.message(Command(commands=['new_admin', 'add_admin']))
async def new_admin_main(message: Message) -> None:
    check = False
    id_ = 0
    if len(message.text.split()) >= 2:
        id_ = message.text.split()[1]
    cursor = await select_from_db(f'SELECT * FROM admins WHERE id={message.from_user.id}')
    if len(cursor) > 0:
        check = True

    try:
        if check and cursor[3]:
            await insert_into_db(f'INSERT INTO admins(id) VALUES({int(id_)})')
            await message.reply('Админ добавлен!')
        else:
            await message.reply('Недостаточно прав❌')

    except ValueError:
        await message.reply('Неверный ID❌')


@dp.message(Command(commands=['execute', 'script', 'insert']))
async def execute(message: Message) -> None:
    if len(message.text.split()) >= 2:
        cmd = ' '.join(message.text.split()[1:])
        cursor = await select_from_db(f'SELECT * FROM admins WHERE id={message.from_user.id}')
        if len(cursor) > 0:
            if cursor[4]:
                await insert_into_db(cmd)
                await message.reply('Выполнено!')
            else:
                await message.reply('Недостаточно прав❌')
        else:
            await message.reply('Недостаточно прав❌')


@dp.message(Command(commands=['select']))
async def select(message: Message) -> None:
    if len(message.text.split()) >= 2:
        cmd = ' '.join(message.text.split()[1:])
        cursor = await select_from_db(f'SELECT * FROM admins WHERE id={message.from_user.id}')
        if len(cursor) > 0:
            if cursor[5]:
                ans = await select_from_db(cmd)
                await message.reply(f'{ans}')
            else:
                await message.reply('Недостаточно прав❌')
        else:
            await message.reply('Недостаточно прав❌')


"""Обработка кнопок (помещена в конец файла т.к. пользователь может передумать и воспользоваться командой)"""


@dp.message(Command(commands=['menu']))
@dp.message(F.text == main_keyboard.keyboard[4][0].text)
async def start_button(message: Message):
    await message.reply(CMD_TEXT, reply_markup=main_keyboard)


@dp.message(Command(commands=['upgrade']))
@dp.message(F.text == main_keyboard.keyboard[2][0].text)
async def upgrade_button_main(message: Message, state: FSMContext):
    num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
    if num is None:
        num = 0
    kol = (await select_from_db(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}'))[0]
    if kol is None:
        kol = 0
    cursor = await select_from_db(
        f'SELECT id, value1, value2, value3 FROM legendary WHERE user_id={message.from_user.id} AND (value1 < 1 OR value2 < 1 OR value3 < 1)')
    if not (type(cursor[0]) is type([])):
        cursor = [cursor]
    keyboard = ReplyKeyboardMarkup(keyboard=[], resize_keyboard=True)
    value = [[KeyboardButton(text='◀️ Отмена')]]
    for i in cursor:
        a = []
        if i[1] < 1:
            lvls = min(kol // price[1], (1 - i[1]) * 10)
            new_value = round(i[1] + 0.1 * lvls, 1)
            a.append(KeyboardButton(text=f'{i[0]} 1\n(с {i[1]} до {new_value})'))
        if i[2] < 1:
            lvls = min(kol // price[1], (1 - i[2]) * 10)
            new_value = round(i[2] + 0.1 * lvls, 1)
            a.append(KeyboardButton(text=f'{i[0]} 2\n(с {i[2]} до {new_value})'))
        if i[3] < 1:
            lvls = min(kol // price[1], (1 - i[3]) * 10)
            new_value = round(i[3] + 0.1 * lvls, 1)
            a.append(KeyboardButton(text=f'{i[0]} 3\n(с {i[3]} до {new_value})'))
        if a:
            value.append(a)
    keyboard.keyboard = value

    await message.reply(f"Введите номер {param2[1]} и номер характеристики через пробел. Всего у вас {param2[7]}: {num}",
                        reply_markup=keyboard)
    await state.set_state(Form1.value)


@dp.message(Form1.value)
async def process_upgrade_button_main(message: Message, state: FSMContext = FSMContext):
    form = await state.update_data(value=message.text)
    num: str = form['value']
    if len(num.split()) >= 2:
        p1 = num.split()[0]
        p2 = num.split()[1]
        await upgrade_main(message, p1, p2)
    else:
        await message.reply("Недостаточно значений❌",
                            reply_markup=main_keyboard)
    await state.clear()


@dp.message(Command(commands=['name']))
@dp.message(F.text == main_keyboard.keyboard[2][1].text)
async def name_button_main(message: Message, state: FSMContext):
    max_num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
    if max_num is None:
        max_num = 0
    board = [[KeyboardButton(text='◀️ Отмена')]]
    for i in range(max_num // 4):
        board.append([KeyboardButton(text=f'{4 * i + x}') for x in range(1, 5)])
    if max_num % 4:
        board.append([KeyboardButton(text=f'{x}') for x in range(max_num // 4 * 4 + 1, max_num + 1)])
    keyboard = ReplyKeyboardMarkup(keyboard=board, resize_keyboard=True)
    await message.reply(f"Введите номер {param2[1]}. Всего у вас {param2[7]}: {max_num}",
                        reply_markup=keyboard)
    await state.set_state(Form2.value)


@dp.message(Form2.value)
async def name_button_main2(message: Message, state: FSMContext):
    form = await state.update_data(value=message.text)
    await message.reply(f'Введите имя {param2[1]}.', reply_markup=cancel_keyboard)
    await state.set_state(Form2.name)


@dp.message(Form2.name)
async def process_name_button_main(message: Message, state: FSMContext):
    form = await state.update_data(name=message.text)
    num = form['value']
    name_ = form['name']
    await naming_main(message, num, name_)
    await state.clear()


@dp.message(F.text == main_keyboard.keyboard[3][0].text)
async def collect_button_main(message: Message, state: FSMContext):
    max_num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
    if max_num is None:
        max_num = 0
    board = [[KeyboardButton(text='◀️ Отмена')]]
    for i in range(max_num // 4):
        board.append([KeyboardButton(text=f'{4 * i + x}') for x in range(1, 5)])
    if max_num % 4:
        board.append([KeyboardButton(text=f'{x}') for x in range(max_num // 4 * 4 + 1, max_num + 1)])
    keyboard = ReplyKeyboardMarkup(keyboard=board, resize_keyboard=True)
    await message.reply(f"Введите номер {param2[1]}. Всего у вас {param2[7]}: {max_num}",
                        reply_markup=keyboard)
    await state.set_state(Form3.value)


@dp.message(Form3.value)
async def process_collect_button_main(message: Message, state: FSMContext):
    form = await state.update_data(value=message.text)
    num: str = form['value']
    id_ = num.split()[0]
    await collect_main(message, id_)
    await state.clear()


@dp.message(Command(commands=['time', 'timezone', 'set_time']))
@dp.message(F.text == main_keyboard.keyboard[4][1].text)
async def time_button_main(message: Message, state: FSMContext):
    await message.reply("Выберите свой часовой пояс из списка",
                        reply_markup=time_keyboard)
    await state.set_state(Form4.value)


@dp.message(Form4.value)
async def process_time_button_main(message: Message, state: FSMContext):
    form = await state.update_data(value=message.text)
    num: str = form['value']
    zones = [y[0].text for y in (x for x in time_keyboard.keyboard)] + [y[1].text for y in (x for x in time_keyboard.keyboard)]
    if num in zones:
        num = str(int(num.split()[0][3:]) - 3)
        await timezone_main(message, num)
    else:
        await message.reply("Неверное значение",
                            reply_markup=main_keyboard)
    await state.clear()


@dp.message(Command(commands=['sell']))
async def sell_main(message: Message, state: FSMContext) -> None:
    num = (await select_from_db(f'SELECT id FROM legendary WHERE user_id={message.from_user.id} AND class1 <> NULL'))[0]
    if len(num) == 0:
        pass
    elif type(num[0]) is type([]):
        num = [x[0] for x in num]
    board = [[KeyboardButton(text='◀️ Отмена')]]
    for i in range(len(num) // 4):
        board.append([KeyboardButton(text=f'{num[4 * i + x]}') for x in range(4)])
    if len(num) % 4:
        board.append([KeyboardButton(text=f'{x}') for x in num[(len(num) // 4 * 4):]])
    keyboard = ReplyKeyboardMarkup(keyboard=board, resize_keyboard=True)
    await message.reply(f'Введите номер {param2[1]}.',
                        reply_markup=keyboard)
    await state.set_state(Form5.value)


@dp.message(Form5.value)
async def sell_main(message: Message, state: FSMContext) -> None:
    form = await state.update_data(value=message.text)
    await message.reply(f'Введите желаемую стоимость {param2[1]}', reply_markup=cancel_keyboard)
    await state.set_state(Form5.cost)


@dp.message(Form5.cost)
async def process_sell_main(message: Message, state: FSMContext) -> None:
    form = await state.update_data(cost=message.text)
    change = False
    num = form['value']
    cost = form['cost']

    try:
        cost = int(cost)
        if cost < 0:
            cost = 0
    except ValueError:
        cost = 0

    max_num = (await select_from_db(f"SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}"))[0]
    if max_num is None:
        max_num = 0

    try:
        if 1 <= int(num) <= max_num:
            class_ = (await select_from_db(
                f"SELECT class1 FROM legendary WHERE id={int(num)} AND user_id={message.from_user.id}"))[0]
            if not (class_ is None):
                change = True
            else:
                await message.reply(f"Этот {param2[0]} не коллекционный❌")
    except ValueError:
        await message.reply("Неверные значения❌\n")

    if change:
        await insert_into_db(
            f"UPDATE legendary SET sell={cost} WHERE id={int(num)} AND user_id={message.from_user.id}")
        if cost > 0:
            await message.reply(f"Цена на {param2[3]} изменена на {cost}{param1[13]}")
        else:
            await message.reply(f"{param2[0].capitalize()} снят с продажи")

    await state.clear()


@dp.message(Command(commands=['promo', 'promocode', 'activate']))
async def activate_button(message: Message, state: FSMContext):
    await message.reply(f'Введите промокод.', reply_markup=cancel_keyboard)
    await state.set_state(Form6.value)


@dp.message(Form6.value)
async def process_activate_button(message: Message, state: FSMContext):
    form = await state.update_data(value=message.text)
    promo = form['value']
    await activate_main(message, promo)
    await state.clear()


"""Стартовое сообщение с списком команд"""


@dp.message(CommandStart())
@dp.message(F.text == main_keyboard.keyboard[0][0].text)
async def start_main(message: Message, command: CommandObject = CommandObject()) -> None:
    if len(await select_from_db(f'SELECT * FROM stat WHERE user_id={message.from_user.id}')) == 0:
        """Запись нового пользователя"""
        await insert_into_db(
            f"INSERT INTO stat(user_id, kol, koff, gets_kol, time, streak, activity) VALUES ({message.from_user.id}, 0, 0, 0, 0, 1, 0)")

    await message.reply(START_TEXT, reply_markup=main_keyboard)

    """Проверка на наличие промокода"""
    if command.args:
        if not ((await get_promo(command.args)) is None):
            await activate_main(message, promo=command.args)


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
            streak = (await select_from_db(f"SELECT streak FROM stat WHERE user_id={message.from_user.id}"))[0] + 1
            tomorrow = await change_timedelta(bonus_date + " 00:00:00", 24)
            if bonus_date == user_date.split()[0]:
                streak -= 1
            elif user_date == tomorrow:
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
    koff = 1
    cursor = await select_from_db(f'SELECT kol, time, promo FROM stat WHERE user_id={message.from_user.id}')
    try:
        balance, timezona, PROMO = cursor[0], cursor[1], cursor[2]
    except IndexError:
        balance, timezona, PROMO = 0, 0, None
        await insert_into_db(
            f"INSERT INTO stat(user_id, kol, koff, gets_kol, time, streak, activity) VALUES ({message.from_user.id}, 0, 0, 0, 0, 1, 0)")

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
        await insert_into_db(f'INSERT INTO legendary(id, user_id, animal, value1, value2, value3, sell) VALUES({
        num}, {message.from_user.id}, "{name_}", {value1}, {value2}, {value3}, 0)')

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
        await insert_into_db(
            f'UPDATE stat SET kol={balance - int(price[0] * koff)} WHERE user_id={message.from_user.id}')
        await insert_into_db(f'INSERT INTO legendary(id, user_id, animal, value1, value2, value3, sell) VALUES({
        num}, {message.from_user.id}, "{name_}", {value1}, {value2}, {value3}, 0)')

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


@dp.message(F.text == main_keyboard.keyboard[3][1].text)
@dp.message(Command(commands=['me']))
async def me_main(message: Message) -> None:
    text1 = ''
    count1 = 0
    text2 = ''
    count2 = 0
    h2 = ""

    """Получение профиля пользователя"""
    prof = await select_from_db(f'SELECT * FROM stat WHERE user_id={message.from_user.id}')
    if len(prof) == 0:
        await insert_into_db(
            f"INSERT INTO stat(user_id, kol, koff, gets_kol, time, streak, activity) VALUES ({message.from_user.id}, 0, 0, 0, 0, 1, 0)")
        prof = await select_from_db(f'SELECT * FROM stat WHERE user_id={message.from_user.id}')
    if not (prof[2] is None):
        h2 = await change_timedelta(prof[2], 2)
        """Преобразование текущего времени к часовому поясу пользователя"""
        dtime = await change_timedelta(datetime.datetime.now().strftime("%d.%m.%Y %X"), prof[5])

        BOOL = (await check_min_datetime(h2, dtime)) != h2
    else:
        BOOL = False

    """Получение информации о легендарных персонажах"""
    cursor = await select_from_db(f'SELECT * FROM legendary WHERE user_id={message.from_user.id} ORDER BY id')
    if len(cursor) == 0:
        pass
    elif not (type(cursor[0]) is type([])):
        cursor = [cursor]
    for row in cursor:
        if row[4]:
            count2 += 1
            text2 += (f'№{row[0]}, {row[2]}{" " + row[3] if row[3] else ""}, '
                      f'{param3[0]}: {row[4] if row[4] else row[5]}, '
                      f'{param3[1]}: {row[6] if row[6] else row[7]}, '
                      f'{param3[2]}: {row[8] if row[8] else row[9]}\n')
        else:
            count1 += 1
            text1 += (f'№{row[0]}, {row[2]}{" " + row[3] if row[3] else ""}, '
                      f'{param3[0]}: {row[4] if row[4] else row[5]}, '
                      f'{param3[1]}: {row[6] if row[6] else row[7]}, '
                      f'{param3[2]}: {row[8] if row[8] else row[9]}\n')

    # dtime = await str_to_datetime(dtime)
    # h2 = await str_to_datetime(h2)
    # delta = h2 - dtime
    # HH = delta.days * 24 + delta.seconds // 3600
    # MM = delta.seconds // 60 - delta.seconds // 3600 * 60
    # HHMM = 'через ' + str(HH) + 'ч ' + str(MM) + 'мин'
    """Ответ пользователю"""
    await message.reply(f'🆔ID: {prof[0]}\n'
                        f'{param1[13]}{param1[7].capitalize()}: {prof[1]}\n'
                        f'🫴Всего получено: {prof[3]} раз{"а" if (prof[3] % 10 in [2, 3, 4] and prof[3] // 10 % 10 != 1) else ""}\n'
                        f'↗️Ваш уровень: {prof[4] + 1} (x{koffs[prof[4]]})\n'
                        f'{"🆙До следующего уровня: " +
                           str(koffs_kol[prof[4] + 1] - prof[3]) if prof[4] + 1 != len(koffs_kol) else ""}\n'
                        f'⏰Следующее получение: {h2 if BOOL else 'уже доступно! /get'}\n'
                        # f'\n⚙️Часовой пояс: МСК{"+" if prof[5] >= 0 else ""}{prof[5]}'
                        )
    if count1 + count2:
        await message.reply(f'{param2[13]}Легендарных {param2[7]}: {count1}\n{text1} \n'
                            f'{param2[14]}Коллекционных {param2[7]}: {count2}\n{text2}')


@dp.message(Command(commands=['market']))
async def market_main(message: Message) -> None:
    msg = message.text.split()
    if len(msg) >= 4:
        if msg[1] in values1 and msg[2] in values2 and msg[3] in values3:
            check = await select_from_db(f'SELECT id, user_id, sell FROM legendary WHERE '
                                         f'class1="{msg[1]}" AND class2="{msg[2]}" AND class3="{msg[3]}" AND sell > 0')
            if len(check) > 0:
                if check[1] != message.from_user.id:
                    balance = (await select_from_db(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}'))[0]
                    if balance is None:
                        balance = 0

                    if balance >= check[2]:
                        kol = (await select_from_db(f'SELECT kol FROM stat WHERE user_id={check[1]}'))[0]
                        if kol is None:
                            kol = 0
                        await insert_into_db(f'UPDATE stat SET kol={kol + check[2]} WHERE user_id={check[1]}')
                        await bot.send_message(check[1], f'{param2[0].capitalize()} №{check[0]} Продан. Зачислено: {check[2]}{param1[13]}')

                        await insert_into_db(f'UPDATE stat SET kol={balance - check[2]} WHERE user_id={message.from_user.id}')
                        num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
                        if num is None:
                            num = 1
                        else:
                            num += 1

                        await insert_into_db(f'UPDATE legendary SET id={num}, user_id={message.from_user.id}, sell=0 WHERE '
                                             f'class1="{msg[1]}" AND class2="{msg[2]}" AND class3="{msg[3]}"')

                        await message.reply(f'{param2[0].capitalize()} куплен{param2[14]}')

                        cursor = await select_from_db(f'SELECT id FROM legendary WHERE user_id={check[1]} AND id > {check[0]}')
                        if not (type(cursor[0]) is type([])):
                            cursor = [cursor]

                        for i in cursor:
                            await insert_into_db(f'UPDATE legendary SET id={i[0] - 1} WHERE id={i[0]} AND user_id={check[1]}')
                    else:
                        await message.reply(f"Недостаточно {param1[7]}❌")
                else:
                    await message.reply(f"Нельзя покупать {param2[9]} у себя❌")
            else:
                await message.reply(f"Такой {param2[0]} не продаётся❌")
        else:
            await message.reply("Неверные значения❌\n"
                                f"Список продающихся {param2[7]} в Маркете:\n"
                                "t.me/share/?url=wuppit_bot%20_ (Добавьте @ в начало)")
    else:
        await message.reply("Недостаточно значений❌")


@dp.inline_query()
async def inline_main(inline_query: InlineQuery):
    query_id = inline_query.id
    ans = []
    v1, v2, v3 = False, False, False
    if inline_query.query:
        query = inline_query.query.split()
        if query[0] in values1:
            v1 = True
        if len(query) >= 2:
            if query[1] in values2:
                v2 = True
            if len(query) >= 3:
                if query[2] in values3:
                    v3 = True

        if v1 and v2 and v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class1="{query[0]}" AND '
                                         f'class2="{query[1]}" AND class3="{query[2]}" AND sell > 0')
        elif v1 and v2 and not v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class1="{query[0]}" AND '
                                         f'class2="{query[1]}" AND sell > 0')
        elif v1 and not v2 and v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class1="{query[0]}" AND '
                                         f'class3="{query[2]}" AND sell > 0')
        elif not v1 and v2 and v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class2="{query[1]}" AND '
                                         f'class3="{query[2]}" AND sell > 0')
        elif v1 and not v2 and not v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class1="{query[0]}" AND sell > 0')
        elif not v1 and v2 and not v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class2="{query[1]}" AND sell > 0')
        elif not v1 and not v2 and v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class3="{query[2]}" AND sell > 0')
        else:
            list_ = await select_from_db("SELECT animal, class1, class2, class3, sell FROM legendary WHERE sell > 0")

        if len(list_) > 0:
            if not (type(list_[0]) is type([])):
                list_ = [list_]
            for i in range(len(list_)):
                a = InlineQueryResultArticle(id=str(i),
                                             type=InlineQueryResultType.ARTICLE,
                                             title=f'{list_[i][0]} за {list_[i][4]}{param1[13]}',
                                             thumbnail_url=emoji[list_[i][0]],
                                             input_message_content=InputTextMessageContent(
                                                 message_text=f'/market {list_[i][1]} {list_[i][2]} {list_[i][3]}'
                                             ),
                                             hide_url=True,
                                             description=f'{param3[0]}: {list_[i][1]}\n'
                                                         f'{param3[1]}: {list_[i][2]}\n'
                                                         f'{param3[2]}: {list_[i][3]}\n')
                ans.append(a)
        else:
            a = InlineQueryResultArticle(id=query_id,
                                         type=InlineQueryResultType.ARTICLE,
                                         title=f'В продаже ничего нет',
                                         description='Попробуйте изменить фильтры',
                                         input_message_content=InputTextMessageContent(
                                             message_text='Это сообщение ничего не делает.'
                                         ),
                                         hide_url=True)
            ans.append(a)
    else:
        a = InlineQueryResultArticle(id=query_id,
                                     type=InlineQueryResultType.ARTICLE,
                                     title=f'Начните ввод',
                                     description='Поставьте любой символ для пропуска фильтра',
                                     input_message_content=InputTextMessageContent(
                                         message_text='Это сообщение ничего не делает.'
                                     ),
                                     hide_url=True)
        ans.append(a)

    await inline_query.answer(ans)


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
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
