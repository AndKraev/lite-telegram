from lite_telegram.bot import TelegramBot
from lite_telegram.exceptions import TelegramException
from lite_telegram.models import Message, Update


class Context:
    def __init__(self, bot: "TelegramBot", update: Update) -> None:
        self.bot = bot
        self.update = update

    @property
    def is_text_message(self) -> bool:
        return self.update.message is not None and self.update.message.text is not None

    @property
    def is_private_chat(self) -> bool:
        return self.update.message is not None and self.update.message.chat.type == "private"

    @property
    def text(self) -> str | None:
        return self.update.message.text if self.is_text_message else None

    def message(self, text: str) -> Message:
        if self.update.message is None:
            raise TelegramException("Message is not found.")

        return self.bot.send_message(self.update.message.chat.id, text)
