from functools import partialmethod
from typing import List, Optional, Union

from exceptions import LiteTelegramException
from models import Message, Update
from request import request


class TelegramBot:
    def __init__(self, token: str, auto_offset: bool = True):
        self.__base_url = f"https://api.telegram.org/bot{token}/"
        self.auto_offset = auto_offset
        self.last_update_id = -1

    def get_updates(
        self, offset: Optional[int] = None, limit: int = 100, timeout: int = 30
    ) -> List[Update]:

        data = {
            "offset": offset or (self.last_update_id + 1),
            "limit": limit,
            "timeout": timeout,
        }

        results = self._get_from_api("getUpdates", data)

        update_ids = map(lambda upd: upd.get("update_id"), results)
        self.last_update_id = max((self.last_update_id, *update_ids))

        return [Update.from_dict(update_json) for update_json in results]

    def send_message(self, chat_id: str, text: str) -> Message:
        """Use this method to send text messages.

        Args:
            chat_id: Unique identifier for the target chat or username of the target channel
                (in the format @channelusername)
            text: Text of the message to be sent, 1-4096 characters after entities parsing
        """

        data = {
            "chat_id": chat_id,
            "text": text,
        }
        result = self._post_to_api("sendMessage", data)
        return Message.from_dict(result)

    def send_animation(
        self, chat_id: Union[int, str], animation: str, caption: Optional[str]
    ) -> Message:

        data = {
            "chat_id": chat_id,
            "animation": animation,
        }
        if caption:
            data["caption"] = caption

        result = self._post_to_api("sendAnimation", data)
        return Message.from_dict(result)

    def _request_api(self, suburl: str, data: dict, method: str) -> Union[dict, List[dict]]:

        url = self.__base_url + suburl
        response = request(url, data, method)

        if not response.get("ok"):
            raise LiteTelegramException("Response from Telegram API is not ok.")

        if "result" in response:
            return response["result"]
        return response.get("results", [])

    _post_to_api = partialmethod(_request_api, method="POST")
    _get_from_api = partialmethod(_request_api, method="GET")


if __name__ == "__main__":
    import os

    bot = TelegramBot(os.environ["TOKEN"], auto_offset=True)
    chat_id_ = os.environ["CHAT_ID"]

    print(bot.send_message(chat_id_, "test"))
    print(bot.get_updates(timeout=0))
    print(bot.get_updates(timeout=0))
