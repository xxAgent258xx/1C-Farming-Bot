import datetime
import aiosqlite
from aiogram import Bot, Dispatcher
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from bot_param import param1, param2, price
from tokens import FARMING_BOT_TOKEN

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
DB_NAME = '1c.db'


"""Меню бота"""
main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='▶️ Старт'), KeyboardButton(text='⬇️ Свернуть меню')],
    [KeyboardButton(text=f'{param1[13]} Получить {param1[9]}'), KeyboardButton(text=f'{param2[13]} Купить {param2[3]}')],
    [KeyboardButton(text=f'{param2[13]} Улучшить {param2[3]}'), KeyboardButton(text=f'{param2[13]} Имя {param2[1]}')],
    [KeyboardButton(text=f'{param2[14]} Коллекционный {param2[0]}'), KeyboardButton(text='👤 Профиль')],
    [KeyboardButton(text='📋 Список команд'), KeyboardButton(text='⚙️ Часовой пояс')]
], resize_keyboard=True)

# main_keyboard.keyboard[0][0].text
time_keyboard = ReplyKeyboardMarkup(keyboard=[
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


async def select_from_db(query: str, db_name=DB_NAME) -> list:
    ans = []
    async with aiosqlite.connect(db_name) as db:
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


async def insert_into_db(query: str, db_name=DB_NAME) -> None:
    async with aiosqlite.connect(db_name) as db:
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
