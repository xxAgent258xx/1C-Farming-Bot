import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
import aiosqlite
import datetime
import logging
import random

from tokens import FARMING_BOT_TOKEN

names = ["Лев", "Тигр", "Мышь", "Лошадь", "Пантера", "Кролик", "Капибара", "Волк", "Лисица", "Хомяк",
         "Утка", "Гусь", "Олень", "Бобёр", "Сова", "Медведь", "Панда", "Кенгуру", "Орёл", "Антилопа",
         "Енот", "Леопард", "Зебра", "Дракон", "Кошка"]
values1 = ["Белая", "Рыжая", "Красная", "Голубая", "Жёлтая", "Малиновая", "Радужная", "Зелёная", "Фиолетовая", "Синяя"]
values2 = ["Белые", "Рыжие", "Красные", "Голубые", "Жёлтые", "Малиновые", "Радужные", "Зелёные", "Фиолетовые", "Синие"]
values3 = ["Полоска", "Клетка", "Пятна", "Цветы", "Камуфляж", "Леопард", "Звёзды", "Фигуры", "Сетка", "Рябь"]

chance = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
koffs = [1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
koffs_kol = [0, 10, 50, 100, 500, 1000, 2500, 5000, 10000, 25000, 50000]
DB_NAME = '1c.db'
TOKEN = FARMING_BOT_TOKEN


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


bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


# 01.01.2025 00:00:00


@dp.message(CommandStart())
async def start(message: Message):
    await message.reply(
        'Добро пожаловать в увлекательную игру!\nЗдесь ты сможешь получать вуппитов и обменивать их на легендарных!\n'
        '📋Список команд:\n/get - получить вуппита🧸\n'
        '/buy - купить легендарного вуппита за 100🧸\n'
        '/upgrade {№} {#} - прокачать легендарного вуппита за 50🧸\n'
        '/collect {№} - сделать полностью прокачанного легендарного вуппита коллекционным за 150🧸\n'
        '/name {№} {""} - задать имя коллекционному вуппиту\n'
        '/me - посмотреть профиль\n'
        '/time {ЧЧ} - сменить разницу времени с МСК\n'
        '\n{№} - номер вуппита, с которым совершается действие\n'
        '{""} - имя вуппита\n'
        '{ЧЧ} - разница во времени от -15 до +11\n'
        '{#} - номер характеристики (1, 2 или 3)'

    )


@dp.message(Command(commands=['get']))
async def get(message: Message):
    lvl_up = False
    value = 0
    new = True
    maybe = False
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                new = False
        if new:
            await db.execute(
                f'INSERT INTO stat(user_id, kol, koff, gets_kol, time) VALUES ({message.from_user.id}, 0, 0, 1, 0)')
            await db.commit()
            kol, last, koff_index, gets_kol, timezona = 0, None, 0, 1, 0
        else:
            async with db.execute(
                    f'SELECT kol, last, gets_kol, koff, time FROM stat WHERE user_id={message.from_user.id}') as cursor:
                async for row in cursor:
                    kol = row[0]
                    last = row[1]
                    gets_kol = row[2] + 1
                    koff_index = row[3]
                    timezona = row[4]
        if int(timezona) >= 0:
            dtime = (datetime.datetime.now() + datetime.timedelta(hours=int(timezona))).strftime("%d.%m.%Y %X")
        else:
            dtime = (datetime.datetime.now() - datetime.timedelta(hours=abs(int(timezona)))).strftime("%d.%m.%Y %X")
        if not (last is None):
            h2 = (datetime.datetime(day=int(last[0:2]), month=int(last[3:5]), year=int(last[6:10]),
                                    hour=int(last[11:13]), minute=int(last[14:16]),
                                    second=int(last[17:19])) + datetime.timedelta(hours=2)).strftime("%d.%m.%Y %X")
        get_kol = koffs[koff_index]
        if koff_index + 1 < len(koffs_kol):
            if gets_kol == koffs_kol[koff_index + 1]:
                koff_index += 1
                lvl_up = True
        if last is None:
            maybe = True
        elif check_min_datetime(dtime, h2) != dtime:
            maybe = True
        if maybe:
            await db.execute(
                f'UPDATE stat SET kol={kol + get_kol}, last="{dtime}", koff={koff_index}, gets_kol={gets_kol} WHERE user_id={message.from_user.id}')
            await db.commit()
            await message.reply(
                f'{message.from_user.full_name}, вы получили {get_kol}🧸\n'
                f'Возвращайтесь через 2 часа. Всего: {kol + get_kol}🧸\n'
                f'{"Новый уровень! " if lvl_up else ""}Ваш уровень: {koff_index + 1} (x{koffs[koff_index]}). {"До следующего уровня: " + str(koffs_kol[koff_index + 1] - gets_kol) if koff_index + 1 != len(koffs_kol) else ""}')
        else:
            await message.reply('Рано получать вуппитов❌')


@dp.message(Command(commands=['buy']))
async def buy(message: Message):
    balance = 0
    num = 1
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                balance = row[0]
        async with db.execute(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                if not (row[0] is None):
                    num = row[0] + 1
                else:
                    num = 1

        if balance >= 100:
            name_ = random.choice(names)
            value1 = random.choice(chance)
            value2 = random.choice(chance)
            value3 = random.choice(chance)
            await db.execute(f'UPDATE stat SET kol={balance - 100} WHERE user_id={message.from_user.id}')
            await db.execute(
                f'INSERT INTO legendary(id, user_id, animal, value1, value2, value3) VALUES({num}, {message.from_user.id}, "{name_}", {value1}, {value2}, {value3})')
            await db.commit()
            await message.reply('Поздравляю с покупкой легендарного вуппита!🎠\n'
                                f'№: {num}\n'
                                f'Животное: {name_}\n'
                                f'Уровень цвета шерсти: {value1}\n'
                                f'Уровень цвета глаза: {value2}\n'
                                f'Уровень узора: {value3}\n\n'
                                f'Прокачайте вуппита до максимального уровня, чтобы сделать коллекционным!')
        else:
            await message.reply('Недостаточно вуппитов❌')


@dp.message(Command(commands=['me']))
async def me(message: Message):
    text = ''
    prof = []
    count = 0
    async with aiosqlite.connect(DB_NAME) as db:
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
            await db.execute(
                f'INSERT INTO stat(user_id, kol, koff, gets_kol, time) VALUES ({message.from_user.id}, 0, 0, 0, 0)')
            await db.commit()
            prof = [message.from_user.id, 0, None, 0, 0, 0]
            BOOL = False

        async with db.execute(f'SELECT * FROM legendary WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                count += 1
                text += f'№{row[0]}, {row[2]}{" " + row[3] if row[3] else ""}, Шерсть: {row[4] if row[4] else row[5]}, Глаза: {row[6] if row[6] else row[7]}, Узор: {row[8] if row[8] else row[9]}\n'

    await message.reply(f'🆔ID: {prof[0]}\n'
                        f'🧸Вуппитов: {prof[1]}\n'
                        f'🧸Всего получено: {prof[3]}\n'
                        f'↗️Ваш уровень: {prof[4] + 1} (x{koffs[prof[4]]})\n'
                        f'{"🆙До следующего уровня: " + str(koffs_kol[prof[4] + 1] - prof[3]) if prof[4] + 1 != len(koffs_kol) else ""}\n'
                        f'⏰Следующее получение: {h2 if BOOL else 'уже доступно! /get'}\n'
                        f'\n⚙️Часовой пояс: МСК{"+" if int(prof[5]) >= 0 else ""}{int(prof[5])}'
                        )
    await message.reply(f'🎠Легендарных вуппитов: {count}\n{text}')
    # print(prof)
    # print(text)


@dp.message(Command(commands=['upgrade']))
async def upgrade(message: Message):
    maybe = False
    num = 0
    text = message.text.split()
    add = ''
    value = 0.0
    kol = 0
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                if row is None:
                    maybe = False
                else:
                    num = row[0]
        try:
            if 1 <= int(text[2]) <= 3 and 1 <= int(text[1]) <= num:
                async with db.execute(
                        f'SELECT value{text[2]} FROM legendary WHERE user_id={message.from_user.id} AND id={text[1]}') as cursor:
                    async for row in cursor:
                        if row is None:
                            maybe = False
                        else:
                            value = row[0]
            else:
                maybe = False
            async with db.execute(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}') as cursor:
                async for row in cursor:
                    if row is None:
                        maybe = False
                    else:
                        kol = row[0]
            if 1 <= int(text[2]) <= 3 and 1 <= int(
                    text[1]) <= num and value <= 0.9 and kol >= 50:
                maybe = True
        except:
            maybe = False

        if maybe:
            if text[2] == '1':
                add = 'Шерсть'
            elif text[2] == '2':
                add = 'Глаза'
            else:
                add = 'Узор'
            await db.execute(f'UPDATE stat SET kol={kol - 50} WHERE user_id={message.from_user.id}')
            await db.execute(
                f'UPDATE legendary SET value{text[2]} = {round(value + 0.1, 1)} WHERE user_id={message.from_user.id} AND id={text[1]}')
            await db.commit()
            await message.reply(f'Вы прокачали {add} до {round(value + 0.1, 1) if value < 0.9 else 1}!\n'
                                f'Ваш баланс: {kol - 50}🧸\n')
        else:
            try:
                if len(text) >= 3:
                    if int(text[1]) > num or int(text[1]) < 1:
                        await message.reply('Неверный номер вуппита❌')
                    elif int(text[2]) > 3 or int(text[2]) < 1:
                        await message.reply('Неверный номер характеристики❌')
                    elif value >= 1.0:
                        await message.reply('Достигнут максимальный уровень❌')
                    elif kol < 50:
                        await message.reply('Недостаточно вуппитов❌')
                else:
                    await message.reply('Недостаточно значений❌')
            except:
                await message.reply('Неверные значения❌')


@dp.message(Command(commands=['collect', 'collectible', 'collected']))
async def collect(message: Message):
    maybe = True
    enable_ = True
    num = 0
    kol = 0
    balance = 0
    check_num = 0
    check_values = 0
    text = message.text.split()
    if len(text) >= 2:
        num = text[1]
    else:
        maybe = False
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT max(id) FROM legendary') as cursor:
            async for row in cursor:
                if row is None:
                    enable_ = True
                else:
                    if len(names) * len(values1) * len(values2) * len(values3) == row[0]:
                        enable_ = False
        async with db.execute(
                f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id} AND id={num}') as cursor:
            async for row in cursor:
                if row is None:
                    maybe = False
                    break
                else:
                    check_num = row[0]
        async with db.execute(
                f'SELECT value1, value2, value3 FROM legendary WHERE user_id={message.from_user.id} AND id={num}') as cursor:
            async for row in cursor:
                if row is None:
                    maybe = False
                    break
                else:
                    check_values = sum(row)
                    if check_values < 3:
                        maybe = False
                        break
        async with db.execute(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}') as cursor:
            async for row in cursor:
                if row is None:
                    maybe = False
                    break
                else:
                    balance = row[0]
                    if balance < 150:
                        maybe = False
                        break
        if maybe and enable_:
            value1 = random.choice(values1)
            value2 = random.choice(values2)
            value3 = random.choice(values3)
            check = True
            async with db.execute(
                    f'SELECT id FROM legendary WHERE class1="{value1}" AND class2="{value2}" AND class3="{value3}"') as cursor:
                async for row in cursor:
                    if row is None:
                        check = True
                    else:
                        check = False
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

            await db.execute(
                f'UPDATE legendary SET class1="{value1}", class2="{value2}", class3="{value3}" WHERE user_id={message.from_user.id} AND id={num}')
            await db.execute(f'UPDATE stat SET kol={balance - 150} WHERE user_id={message.from_user.id}')
            await db.commit()
            await message.reply(f'Вуппит №{num} стал коллекционным!\n'
                                f'Шерсть: {value1}\n'
                                f'Глаза: {value2}\n'
                                f'Узор: {value3}\n'
                                f'Ваш баланс: {balance - 150}🧸')
        elif not enable_:
            await message.reply('Коллекционные вуппиты закончились❌')
        else:
            await message.reply('Неверные значения❌')


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


@dp.message(Command(commands=['name']))
async def naming(message: Message):
    if len(message.text.split()) >= 3:
        id_ = message.text.split()[1]
        name_ = ' '.join(message.text.split()[2:])
        count = 0
        async with (aiosqlite.connect(DB_NAME) as db):
            async with db.execute(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}') as cursor:
                async for kol in cursor:
                    if not (kol[0] is None):
                        count = kol[0]
                    else:
                        count = 0
            try:
                if count > 0:
                    if 1 <= int(id_) <= count:
                        BOOL = '"' in name_ or "'" in name_ or ')' in name_ or '}' in name_ or '--' in name_ or '=' in name_ or \
                            'union' in name_.lower() or 'concat' in name_.lower() or '*' in name_ or ';' in name_ or '@' in name_ or \
                            '|' in name_ or '%' in name_ or '#' in name_ or 'select' in name_.lower() or 'where' in name_.lower() or \
                            '/' in name_ or 'delete' in name_.lower()
                        if not BOOL:
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
                    await message.reply('Нет легендарных вуппитов❌')
            except:
                await message.reply('Неверный ID❌')
    else:
        await message.reply('Недостаточно значений❌')


@dp.message(Command(commands=['time', 'timezone', 'set_time']))
async def timezone(message: Message):
    if len(message.text.split()) >= 2:
        timer = message.text.split()[1]
        last = None
        old_time = 0
        new = True
        async with aiosqlite.connect(DB_NAME) as db:
            try:
                if -15 <= int(timer) <= 11:
                    async with db.execute(f'SELECT last, time FROM stat WHERE user_id={message.from_user.id}') as cursor:
                        async for row in cursor:
                            last = row[0]
                            old_time = row[1]

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
                    async with db.execute(f'SELECT time FROM stat WHERE user_id={message.from_user.id}') as cursor:
                        async for row in cursor:
                            new = False
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
            async for ADMIN_ID in cursor:
                await bot.send_message(ADMIN_ID[0], f'Бот @{bot_info.username} включён')


async def on_shutdown():
    bot_info = await bot.get_me()
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(f'SELECT * FROM admins') as cursor:
            async for ADMIN_ID in cursor:
                await bot.send_message(ADMIN_ID[0], f'Бот @{bot_info.username} выключен')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
