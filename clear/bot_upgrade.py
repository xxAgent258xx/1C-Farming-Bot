import datetime
from aiogram.types import Message

from bot_param import param1, param2, param3, price
from bot_const import (select_from_db, change_timedelta, check_min_datetime,
                       get_promo, insert_into_db, main_keyboard)


async def upgrade(message: Message, p1="", p2="") -> None:
    status = "OK"
    num = 0
    text = message.text.split()
    add = ''
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
    if kol < int(price[1] * koff):
        status = f"Недостаточно {param1[7]}❌"

    if status == "OK":
        """Запись в БД, ответ пользователю"""
        add = param3[5 + int(p2)]

        await insert_into_db(f'UPDATE stat SET kol={kol - int(price[1] * koff)} WHERE user_id={message.from_user.id}')
        await insert_into_db(
            f'UPDATE legendary SET value{p2} = {round(value + 0.1, 1)} WHERE user_id={message.from_user.id} AND id={p1}')

        await message.reply(f'Вы прокачали {add} до {round(value + 0.1, 1)}!\n'
                            f'Ваш баланс: {kol - int(price[1] * koff)}{param1[13]}\n', reply_markup=main_keyboard)
    else:
        await message.reply(status, reply_markup=main_keyboard)
