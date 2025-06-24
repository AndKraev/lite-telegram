import asyncio
import logging
from datetime import datetime

import loguru

from lite_telegram.context import Context
from lite_telegram.types import FilterCallable


class LoguruTenacityAdapter(logging.Logger):
    def __init__(self, loguru_logger: "loguru.Logger"):
        super().__init__(name="adapter")
        self.loguru_logger = loguru_logger

    def log(self, level: int, *args, **kwargs) -> None:
        self.loguru_logger.log(logging.getLevelName(level), *args, **kwargs)


async def sleep_until(dt: datetime) -> None:
    sleep_time = dt - datetime.now()
    await asyncio.sleep(sleep_time.seconds)


def allowed_chats(chat_ids: int | str | list[int | str]) -> FilterCallable:
    if isinstance(chat_ids, (int, str)):
        chat_ids = [chat_ids]

    chat_ids = [int(chat_id) for chat_id in chat_ids]

    async def wrapper(ctx: Context) -> bool:
        return ctx.is_text_message and ctx.update.message.chat.id in chat_ids

    return wrapper
