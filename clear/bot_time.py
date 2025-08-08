from aiogram.types import Message
from bot_const import (select_from_db, change_timedelta, insert_into_db,
                       main_keyboard)


async def timezone(message: Message, timer="") -> None:
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
