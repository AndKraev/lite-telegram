from typing import Awaitable, Callable

from lite_telegram.bot import TelegramBot
from lite_telegram.models import Update

UpdateRunnable = Callable[[TelegramBot, Update], Awaitable[None]]
ScheduleRunnable = Callable[[], Awaitable[None]]
