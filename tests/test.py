import asyncio
import os

import httpx

from lite_telegram.bot import TelegramBot
from lite_telegram.handler import TelegramHandler
from lite_telegram.models import Update
from lite_telegram.utils import is_command

TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


async def command_hello(bot: TelegramBot, update: Update) -> None:
    if is_command("/hello", update) and update.message.chat.id == TELEGRAM_CHAT_ID:
        await bot.send_message(update.message.chat.id, "Hello command!")


async def command_sleep(bot: TelegramBot, update: Update) -> None:
    if is_command("/sleep", update) and update.message.chat.id == TELEGRAM_CHAT_ID:
        await bot.send_message(update.message.chat.id, "Starting sleep!")
        await asyncio.sleep(30)
        await bot.send_message(update.message.chat.id, "Finished sleep!")


def every_min_(bot: TelegramBot):
    async def every_min():
        await bot.send_message(TELEGRAM_CHAT_ID, "schedule every min!")

    return every_min




async def main():
    async with httpx.AsyncClient() as aclient:
        bot = TelegramBot(aclient, TELEGRAM_TOKEN)

        # await bot.send_message(TELEGRAM_CHAT_ID, "hi")

        handler = TelegramHandler(bot)
        handler.add_update_handler(command_hello)
        handler.add_update_handler(command_sleep)
        handler.schedule("* * * * *", every_min_(bot))
        await handler.run()





if __name__ == "__main__":
    asyncio.run(main())
