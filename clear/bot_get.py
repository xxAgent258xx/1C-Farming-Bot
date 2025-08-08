import datetime
import random
from aiogram.types import Message

from bot_param import param1
from bot_const import (select_from_db, change_timedelta, check_min_datetime,
                       str_to_datetime, get_promo, koffs, koffs_kol, chance,
                       insert_into_db)


async def get(message: Message) -> None:
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
