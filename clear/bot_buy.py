import datetime
import random
from aiogram.types import Message

from bot_param import param1, param2, param3, price, names
from bot_const import (select_from_db, change_timedelta, check_min_datetime,
                       get_promo, chance, insert_into_db, add2, add4, add5)


async def buy(message: Message, promo=0) -> None:
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
        await insert_into_db(f'UPDATE stat SET kol={balance - int(price[0] * koff)} WHERE user_id={message.from_user.id}')
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
