from typing import Any

from lite_telegram.bot import TelegramBot
from lite_telegram.exceptions import TelegramException
from lite_telegram.models import Message, Update


class Context:
    _params: dict[str, Any] = {}

    def __init__(self, bot: TelegramBot, update: Update) -> None:
        self.bot = bot
        self.update = update

    @property
    def is_text_message(self) -> bool:
        return self.update.message is not None and self.update.message.text is not None
    
    @property
    def is_command(self) -> bool:
        return self.is_text_message and self.text.startswith("/") and len(self.text) > 1

    @property
    def is_private_chat(self) -> bool:
        return self.update.message is not None and self.update.message.chat.type == "private"

    @property
    def text(self) -> str | None:
        return self.update.message.text if self.is_text_message else None

    def reply(self, text: str) -> Message:
        if self.update.message is None:
            raise TelegramException("Context is not a message.")

        return self.bot.send_message(self.update.message.chat.id, text)
    
    def set(self, key: str, value: Any) -> None:
        self._params[key] = value
    
    def get(self, key: str, default: Any | None = None) -> Any | None:
        return self._params.get(key, default)
