import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from croniter import croniter
from loguru import logger

from lite_telegram.bot import TelegramBot
from lite_telegram.context import Context
from lite_telegram.types import FilterCallable, HandlerCallable, ScheduleCallable
from lite_telegram.utils import sleep_until


@dataclass
class ScheduleTask:
    cron: str
    runnable_task: ScheduleCallable
    random_delay: timedelta | None = None


class Handler:
    def __init__(
        self,
        bot: TelegramBot,
        global_filter: FilterCallable | None,
        poll_interval: int = 60,
        allowed_updates: list[str] | None = None,
    ) -> None:
        self.bot = bot
        self.poll_interval = poll_interval
        self.allowed_updates = allowed_updates
        self.global_filter = global_filter

        self._handlers: dict[str, HandlerCallable] = {}
        self._schedule_tasks: list[ScheduleTask] = []

    def add_handler(self, alias: str, handler: HandlerCallable) -> None:
        self._handlers[alias] = handler

    def schedule(
        self, cron: str, task: ScheduleCallable, random_delay: timedelta | None = None
    ) -> None:
        self._schedule_tasks.append(ScheduleTask(cron, task, random_delay))

    async def start(self) -> None:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._run_handlers())
            tg.create_task(self._run_scheduler())

    async def _run_handlers(self) -> None:
        async with asyncio.TaskGroup() as tg:
            while True:
                for update in await self.bot.get_updates(self.poll_interval, self.allowed_updates):
                    context = Context(self.bot, update)
                    if self.global_filter is None or self.global_filter(context):
                        tg.create_task(self._handle_update(context))

    async def _handle_update(self, context: Context) -> None:
        if context.is_text_message is not None:
            handler = self._handlers.get(context.text.strip())

            if handler is not None:
                await handler(context)

    async def _run_scheduler(self) -> None:
        async with asyncio.TaskGroup() as tg:
            for task in self._schedule_tasks:
                tg.create_task(self._run_scheduled_task(task))

    async def _run_scheduled_task(self, task: ScheduleTask) -> None:
        task_name = task.runnable_task.__name__

        for next_run in croniter(task.cron, datetime.now()).all_next(datetime):
            if task.random_delay is not None:
                next_run += timedelta(seconds=random.randint(0, task.random_delay.seconds))

            logger.info("Scheduled task '{}' will start at {}.", task_name, next_run)
            await sleep_until(next_run)

            logger.info("Starting scheduled task '{}'.", task_name)
            await task.runnable_task(self.bot)
            logger.info("Finished scheduled task '{}'.", task_name)
