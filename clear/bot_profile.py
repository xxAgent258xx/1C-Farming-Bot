import datetime
from aiogram.types import Message

from bot_param import param1, param2, param3
from bot_const import (select_from_db, change_timedelta, check_min_datetime,
                       koffs, koffs_kol)


async def me(message: Message) -> None:
    text1 = ''
    count1 = 0
    text2 = ''
    count2 = 0
    h2 = ""

    """Получение профиля пользователя"""
    prof = await select_from_db(f'SELECT * FROM stat WHERE user_id={message.from_user.id}')
    if not (prof[2] is None):
        h2 = await change_timedelta(prof[2], 2)
        """Преобразование текущего времени к часовому поясу пользователя"""
        dtime = await change_timedelta(datetime.datetime.now().strftime("%d.%m.%Y %X"), prof[5])

        BOOL = (await check_min_datetime(h2, dtime)) != h2
    else:
        BOOL = False

    """Получение информации о легендарных персонажах"""
    cursor = await select_from_db(f'SELECT * FROM legendary WHERE user_id={message.from_user.id}')
    if len(cursor) == 0:
        pass
    elif type(cursor[0]) is type([]):
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
    else:
        if cursor[4]:
            count2 = 1
            text2 = (f'№{cursor[0]}, {cursor[2]}{" " + cursor[3] if cursor[3] else ""}, '
                     f'{param3[0]}: {cursor[4] if cursor[4] else cursor[5]}, '
                     f'{param3[1]}: {cursor[6] if cursor[6] else cursor[7]}, '
                     f'{param3[2]}: {cursor[8] if cursor[8] else cursor[9]}\n')
        else:
            count1 = 1
            text1 = (f'№{cursor[0]}, {cursor[2]}{" " + cursor[3] if cursor[3] else ""}, '
                     f'{param3[0]}: {cursor[4] if cursor[4] else cursor[5]}, '
                     f'{param3[1]}: {cursor[6] if cursor[6] else cursor[7]}, '
                     f'{param3[2]}: {cursor[8] if cursor[8] else cursor[9]}\n')

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
