import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from croniter import croniter
from loguru import logger

from lite_telegram.bot import TelegramBot
from lite_telegram.types import ScheduleRunnable, UpdateRunnable
from lite_telegram.utils import sleep_until


@dataclass
class ScheduleTask:
    cron: str
    runnable_task: ScheduleRunnable
    random_delay: timedelta | None


class TelegramHandler:
    def __init__(self, bot: TelegramBot) -> None:
        self.bot = bot

        self._update_handlers: list[UpdateRunnable] = []
        self._schedule_tasks: list[ScheduleTask] = []

    def add_update_handler(self, update_handler: UpdateRunnable) -> None:
        self._update_handlers.append(update_handler)

    def schedule(
        self, cron: str, task_runnable: ScheduleRunnable, random_delay: timedelta = None
    ) -> None:
        self._schedule_tasks.append(ScheduleTask(cron, task_runnable, random_delay))

    async def run(
        self, update_timeout: int = 300, allowed_updates: list[str] | None = None
    ) -> None:
        async with asyncio.TaskGroup() as atg:
            atg.create_task(self._run_bot_updates(update_timeout, allowed_updates))
            atg.create_task(self._run_scheduler())

    async def _run_bot_updates(
        self, timeout: int = 300, allowed_updates: list[str] | None = None
    ) -> None:
        async with asyncio.TaskGroup() as tg:
            while True:
                for update in await self.bot.get_updates(timeout, allowed_updates):
                    tg.create_task(self._handle_update(update))

    async def _handle_update(self, update) -> None:
        async with asyncio.TaskGroup() as tg:
            for handler in self._update_handlers:
                tg.create_task(handler(self.bot, update))

    async def _run_scheduler(self) -> None:
        async with asyncio.TaskGroup() as atg:
            for task in self._schedule_tasks:
                atg.create_task(self._run_schedule(task))

    async def _run_schedule(self, task: ScheduleTask) -> None:
        for next_run in croniter(task.cron, datetime.now()).all_next(datetime):
            if task.random_delay is not None:
                randoms_secs = random.randint(0, task.random_delay.seconds)
                next_run += timedelta(seconds=randoms_secs)

            logger.info(
                "Scheduled task '{}' will start at {}.", task.runnable_task.__name__, next_run
            )
            await sleep_until(next_run)

            logger.info("Starting scheduled task '{}'.", task.runnable_task.__name__)
            await task.runnable_task()
            logger.info("Finished scheduled task '{}'.", task.runnable_task.__name__)
