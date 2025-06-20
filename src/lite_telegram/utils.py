import asyncio
import logging
from datetime import datetime

import loguru


class LoguruTenacityAdapter(logging.Logger):
    def __init__(self, loguru_logger: "loguru.Logger"):
        super().__init__(name="adapter")
        self.loguru_logger = loguru_logger

    def log(self, level: int, *args, **kwargs) -> None:
        self.loguru_logger.log(logging.getLevelName(level), *args, **kwargs)


async def sleep_until(dt: datetime) -> None:
    sleep_time = dt - datetime.now()
    await asyncio.sleep(sleep_time.seconds)
