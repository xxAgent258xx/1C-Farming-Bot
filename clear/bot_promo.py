import datetime
from aiogram.types import Message

from bot_buy import buy
from bot_param import param1
from bot_const import (select_from_db, change_timedelta, get_promo, insert_into_db)


async def activate(message: Message, promo="") -> None:
    bonus = False

    """Проверка, отсутствует ли активированный промокод"""
    if (await select_from_db(f"SELECT promo FROM stat WHERE user_id={message.from_user.id}"))[0] is None:
        """Проверка, был ли передан промокод"""
        if promo == "":
            text = message.text.split()
            if len(text) >= 2:
                promo = text[1]
                if not ((await get_promo(promo)) is None):
                    bonus = await get_promo(promo)
                else:
                    await message.reply("Промокод не найден❌")
            else:
                await message.reply("Промокод не введён❌")
        else:
            bonus = await get_promo(promo)

        if bonus:
            """Преобразование текущего времени к часовому поясу пользователя"""
            timezona = (await select_from_db(f"SELECT time FROM stat WHERE user_id={message.from_user.id}"))[0]
            dtime = await change_timedelta(datetime.datetime.now().strftime("%d.%m.%Y %X"), timezona)

            """Отделение даты"""
            dtime = dtime.split()[0]

            """Запись промокода и даты активации"""
            await insert_into_db(f'UPDATE stat SET promo="{promo};{dtime}" WHERE user_id={message.from_user.id}')

            """Выдача вознаграждений"""
            keys = list(bonus.keys())
            if "balance" in keys:
                kol = await select_from_db(f"SELECT kol FROM stat WHERE user_id={message.from_user.id}")
                await insert_into_db(f"UPDATE stat SET kol={kol[0] + bonus["balance"]} WHERE user_id={message.from_user.id}")
                await message.reply(f"Зачислено {bonus["balance"]}{param1[13]}")
            if "buy" in keys:
                await buy(message, promo=bonus["buy"])

    else:
        await message.reply("Вы уже активировали промокод❌")
