from aiogram.types import Message
from bot_const import (select_from_db, insert_into_db)


async def new_admin(message: Message) -> None:
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


async def execute(message: Message) -> None:
    cmd = ""
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


async def select(message: Message) -> None:
    cmd = ""
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
