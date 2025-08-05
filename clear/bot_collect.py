import datetime
import random
from aiogram.types import Message

from bot_param import (param1, param2, param3, values1, values2, values3,
                       names, price)
from bot_const import (select_from_db, change_timedelta, check_min_datetime,
                       get_promo, add2, insert_into_db, main_keyboard)


async def collect(message: Message, num_="") -> None:
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
        await insert_into_db(f'UPDATE stat SET kol={balance - int(price[2] * koff)} WHERE user_id={message.from_user.id}')
        await message.reply(f'{param2[0].capitalize()} №{num} стал коллекционн{add2}!{param2[14]}\n'
                            f'{param3[0]}: {value1}\n'
                            f'{param3[1]}: {value2}\n'
                            f'{param3[2]}: {value3}\n'
                            f'Ваш баланс: {balance - int(price[2] * koff)}{param1[13]}',
                            reply_markup=main_keyboard)
    else:
        await message.reply(status, reply_markup=main_keyboard)
