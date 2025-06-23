import asyncio
import os

import httpx

from lite_telegram.bot import TelegramBot
from lite_telegram.handler import Handler
from lite_telegram.context import Context

TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")


async def command_hello(context: Context) -> None:
    await context.reply("hello")

async def every_min(bot: TelegramBot):
    await bot.send_message(TELEGRAM_CHAT_ID, "schedule every min!")


async def main():
    async with httpx.AsyncClient() as aclient:
        bot = TelegramBot(aclient, TELEGRAM_TOKEN)

        # await bot.send_message(TELEGRAM_CHAT_ID, "hi")

        is_allowed_chat = lambda ctx: (
            ctx.update.message is not None and ctx.update.message.chat.id == TELEGRAM_CHAT_ID
        )
        handler = Handler(bot, is_allowed_chat)
        handler.add_handler("/hello", command_hello)
        handler.schedule("* * * * *", every_min)
        await handler.start()


if __name__ == "__main__":
    asyncio.run(main())
