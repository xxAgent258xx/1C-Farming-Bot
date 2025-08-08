from aiogram.types import Message

from bot_const import bot
from bot_param import param2
from bot_const import select_from_db, insert_into_db, main_keyboard


async def naming(message: Message, id_="", name_="") -> None:
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
                    """Запись в БД, ответ пользователю"""
                    await insert_into_db(
                            f'UPDATE legendary SET name={name_} WHERE id={id_} AND user_id={message.from_user.id}')
                    await message.reply('Имя изменено!',
                                        reply_markup=main_keyboard)
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
