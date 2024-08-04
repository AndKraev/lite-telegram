from typing import List, Optional, Union

import request
from exceptions import LiteTelegramException
from models import Message, Update


class TelegramBot:
    def __init__(self, token: str, auto_offset: bool = True):
        self.__base_url = f"https://api.telegram.org/bot{token}/"
        self.auto_offset = auto_offset
        self.last_update_id = -1

    def get_updates(
        self, offset: Optional[int] = None, limit: int = 100, timeout: int = 30
    ) -> List[Update]:

        url = self.__base_url + "getUpdates"
        data = {
            "offset": offset or (self.last_update_id + 1),
            "limit": limit,
            "timeout": timeout,
        }

        response = request.get(url, data)
        if not response.get("ok"):
            raise LiteTelegramException("Response from Telegram API is not ok.")

        update_jsons = response.get("result", [])

        update_ids = map(lambda upd: upd.get("update_id"), update_jsons)
        self.last_update_id = max((self.last_update_id, *update_ids))

        return [Update.from_dict(update_json) for update_json in update_jsons]

    def send_message(self, chat_id: str, text: str) -> Message:
        url = self.__base_url + "sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
        }
        response = request.post(url, data)
        if not response.get("ok"):
            raise LiteTelegramException("Response from Telegram API is not ok.")

        return Message.from_dict(response.get("result"))

    def send_animation(
        self, chat_id: Union[int, str], animation: str, caption: Optional[str]
    ) -> Message:
        url = self.__base_url + "sendAnimation"
        data = {
            "chat_id": chat_id,
            "animation": animation,
        }
        if caption:
            data["caption"] = caption

        response = request.post(url, data)
        if not response.get("ok"):
            raise LiteTelegramException("Response from Telegram API is not ok.")

        return Message.from_dict(response.get("result"))


if __name__ == "__main__":
    import os

    bot = TelegramBot(os.environ["TOKEN"], auto_offset=True)
    chat_id_ = os.environ["CHAT_ID"]

    print(bot.send_message(chat_id_, "test"))
    print(bot.get_updates(timeout=0))
    print(bot.get_updates(timeout=0))
