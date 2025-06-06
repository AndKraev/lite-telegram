import asyncio
import logging
from datetime import datetime

import loguru

from lite_telegram.models import Update


class LoguruTenacityAdapter(logging.Logger):
    def __init__(self, loguru_logger: "loguru.Logger"):
        super().__init__(name="adapter")
        self.loguru_logger = loguru_logger

    def log(self, level: int, *args, **kwargs) -> None:
        self.loguru_logger.log(logging.getLevelName(level), *args, **kwargs)


def is_text_message(update: Update) -> bool:
    return update.message is not None and update.message.text is not None


def is_command(alias: str, update: Update) -> bool:
    alias = alias.lower()
    if not alias.startswith("/"):
        alias = "/" + alias

    return is_text_message(update) and update.message.text.strip().lower() == alias


async def sleep_until(dt: datetime) -> None:
    sleep_time = dt - datetime.now()
    await asyncio.sleep(sleep_time.seconds)
