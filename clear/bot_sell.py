from aiogram.types import (Message, InlineQuery, InlineQueryResultArticle,
                           InputTextMessageContent)
from aiogram.enums import InlineQueryResultType
from bot_param import param1, param2, param3, values1, values2, values3
from bot_const import select_from_db, insert_into_db, bot


async def sell(message: Message) -> None:
    change = False
    price = 0

    if len(message.text.split()) >= 2:
        num = message.text.split()[1]
        max_num = (await select_from_db(f"SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}"))[0]
        if max_num is None:
            max_num = 0

        try:
            if 1 <= int(num) <= max_num:
                class_ = (await select_from_db(f"SELECT class1 FROM legendary WHERE id={int(num)} AND user_id={message.from_user.id}"))[0]
                if not (class_ is None):
                    change = True
                else:
                    await message.reply(f"Этот {param2[0]} не коллекционный❌")
        except ValueError:
            await message.reply("Неверные значения❌\n"
                                "Пример команды: /sell 1 100\n"
                                "/sell 1 0")

        if len(message.text.split()) >= 3:
            try:
                price = int(message.text.split()[2])
                if price < 0:
                    price = 0
            except ValueError:
                price = 0

        if change:
            await insert_into_db(
                f"UPDATE legendary SET sell={price} WHERE id={int(num)} AND user_id={message.from_user.id}")
            if price > 0:
                await message.reply(f"Цена на {param2[3]} изменена на {price}{param1[13]}")
            else:
                await message.reply(f"{param2[0].capitalize()} снят с продажи")
    else:
        await message.reply("Недостаточно значений❌\n"
                            "Пример команды: /sell 1 100\n"
                            "/sell 1 0")


async def inline(inline_query: InlineQuery):
    query_id = inline_query.id
    ans = []
    v1, v2, v3 = False, False, False
    if inline_query.query:
        query = inline_query.query.split()
        if query[0] in values1:
            v1 = True
        if len(query) >= 2:
            if query[1] in values2:
                v2 = True
            if len(query) >= 3:
                if query[2] in values3:
                    v3 = True

        if v1 and v2 and v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class1="{query[0]}" AND '
                                         f'class2="{query[1]}" AND class3="{query[2]}" AND sell > 0')
        elif v1 and v2 and not v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class1="{query[0]}" AND '
                                         f'class2="{query[1]}" AND sell > 0')
        elif v1 and not v2 and v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class1="{query[0]}" AND '
                                         f'class3="{query[2]}" AND sell > 0')
        elif not v1 and v2 and v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class2="{query[1]}" AND '
                                         f'class3="{query[2]}" AND sell > 0')
        elif v1 and not v2 and not v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class1="{query[0]}" AND sell > 0')
        elif not v1 and v2 and not v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class2="{query[1]}" AND sell > 0')
        elif not v1 and not v2 and v3:
            list_ = await select_from_db(f'SELECT animal, class1, class2, class3, sell '
                                         f'FROM legendary WHERE class3="{query[2]}" AND sell > 0')
        else:
            list_ = await select_from_db("SELECT animal, class1, class2, class3, sell FROM legendary WHERE sell > 0")

        if len(list_) > 0:
            if not (type(list_[0]) is type([])):
                list_ = [list_]
            for i in range(len(list_)):
                a = InlineQueryResultArticle(id=str(i),
                                             type=InlineQueryResultType.ARTICLE,
                                             title=f'{list_[i][0]} за {list_[i][4]}{param1[13]}',
                                             thumbnail_url='https://emojigraph.org/media/apple/teddy-bear_1f9f8.png',
                                             input_message_content=InputTextMessageContent(
                                                 message_text=f'/market {list_[i][1]} {list_[i][2]} {list_[i][3]}'
                                             ),
                                             hide_url=True,
                                             description=f'{param3[0]}: {list_[i][1]}\n'
                                                         f'{param3[1]}: {list_[i][2]}\n'
                                                         f'{param3[2]}: {list_[i][3]}\n')
                ans.append(a)
        else:
            a = InlineQueryResultArticle(id=query_id,
                                         type=InlineQueryResultType.ARTICLE,
                                         title=f'В продаже ничего нет.',
                                         input_message_content=InputTextMessageContent(
                                             message_text='Это сообщение ничего не делает.'
                                         ),
                                         hide_url=True)
            ans.append(a)
    else:
        a = InlineQueryResultArticle(id=query_id,
                                     type=InlineQueryResultType.ARTICLE,
                                     title=f'Начните ввод.',
                                     input_message_content=InputTextMessageContent(
                                         message_text='Это сообщение ничего не делает.'
                                     ),
                                     hide_url=True)
        ans.append(a)

    await inline_query.answer(ans)


async def market(message: Message) -> None:
    msg = message.text.split()
    if len(msg) >= 4:
        if msg[1] in values1 and msg[2] in values2 and msg[3] in values3:
            check = await select_from_db(f'SELECT id, user_id, sell FROM legendary WHERE '
                                         f'class1="{msg[1]}" AND class2="{msg[2]}" AND class3="{msg[3]}" AND sell > 0')
            if len(check) > 0:
                if check[1] != message.from_user.id:
                    balance = (await select_from_db(f'SELECT kol FROM stat WHERE user_id={message.from_user.id}'))[0]
                    if balance is None:
                        balance = 0

                    if balance >= check[2]:
                        kol = (await select_from_db(f'SELECT kol FROM stat WHERE user_id={check[1]}'))[0]
                        if kol is None:
                            kol = 0
                        await insert_into_db(f'UPDATE stat SET kol={kol + check[2]} WHERE user_id={check[1]}')
                        await bot.send_message(check[1], f'{param2[0].capitalize()} №{check[0]} Продан. Зачислено: {check[2]}{param1[13]}')

                        await insert_into_db(f'UPDATE stat SET kol={balance - check[2]} WHERE user_id={message.from_user.id}')
                        num = (await select_from_db(f'SELECT max(id) FROM legendary WHERE user_id={message.from_user.id}'))[0]
                        if num is None:
                            num = 1
                        else:
                            num += 1

                        await insert_into_db(f'UPDATE legendary SET id={num}, user_id={message.from_user.id} WHERE '
                                             f'class1="{msg[1]}" AND class2="{msg[2]}" AND class3="{msg[3]}"')

                        await message.reply(f'{param2[0].capitalize()} куплен{param2[14]}')

                        cursor = await select_from_db(f'SELECT id FROM legendary WHERE user_id={check[1]} AND id > {check[0]}')
                        if not (type(cursor[0]) is type([])):
                            cursor = [cursor]

                        for i in cursor:
                            await insert_into_db(f'UPDATE legendary SET id={i[0] - 1} WHERE id={i[0]} AND user_id={check[1]}')
                    else:
                        await message.reply(f"Недостаточно {param1[7]}❌")
                else:
                    await message.reply(f"Нельзя покупать {param2[9]} у себя❌")
            else:
                await message.reply(f"Такой {param2[0]} не продаётся❌")
        else:
            await message.reply("Неверные значения❌")
    else:
        await message.reply("Недостаточно значений❌")
