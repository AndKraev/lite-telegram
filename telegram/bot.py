from typing import Any, Dict, List, Optional, Union

import httpx
from exceptions import LiteTelegramException
from models import Message, Update
from pydantic import ValidationError

URL_TEMPLATE = "https://api.telegram.org/bot{token}/{method}"


class TelegramBot:
    _client: Optional[httpx.AsyncClient] = None
    _count = 0

    def __init__(self, token: str):
        self.__token = token
        self._offset = 0

    async def get_updates(
        self, timeout: int = 600, allowed_updates: Optional[List[str]] = None
    ) -> List[Update]:

        data = {"offset": self._offset, "timeout": timeout}
        if allowed_updates:
            data["allowed_updates"] = allowed_updates

        request_timeout = max(int(timeout * 1.5), 30)
        update_data = await self._request("getUpdates", data, request_timeout)

        try:
            updates = [Update.model_validate(update_dict) for update_dict in update_data]
        except ValidationError:
            raise LiteTelegramException(f"Failed to validate update: {ValidationError}")

        self._offset = max((update.update_id + 1 for update in updates), default=self._offset)

        return updates

    async def send_message(self, chat_id: str, text: str, timeout: int = 60) -> Message:
        data = {"chat_id": chat_id, "text": text}
        data = await self._request("sendMessage", data, timeout)
        return Message.model_validate(data)

    async def send_animation(
        self, chat_id: Union[int, str], animation: str, caption: Optional[str], timeout: int = 60
    ) -> Message:

        data = {"chat_id": chat_id, "animation": animation}
        if caption:
            data["caption"] = caption

        data = await self._request("sendAnimation", data, timeout)
        return Message.model_validate(data)

    async def _request(self, method: str, data: Dict[str, Any], timeout: int) -> Any:
        url = URL_TEMPLATE.format(token=self.__token, method=method)
        request_method = "get" if method.startswith("get") else "post"

        try:
            response = await TelegramBot._client.request(
                method=request_method, url=url, data=data, timeout=timeout
            )
            response.raise_for_status()
            data = response.json()
        except httpx.RequestError as exc:
            raise LiteTelegramException(f"Request to TelegramApi failed: {exc}.")

        if not isinstance(data, dict) or "ok" not in data:
            raise LiteTelegramException(f"Incorrect json format from TelegramApi: {data}.")

        if not data["ok"]:
            description = data.get("description")
            raise LiteTelegramException(f"The response is not ok from TelegramApi: {description}.")

        return data.get("result")

    async def __aenter__(self):
        if TelegramBot._client is None:
            TelegramBot._client = httpx.AsyncClient()

        TelegramBot._count += 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        TelegramBot._count -= 1
        if TelegramBot._count <= 0:
            await TelegramBot._client.aclose()


if __name__ == "__main__":
    import asyncio
    import os

    token = os.environ["TOKEN"]
    chat_id_ = os.environ["CHAT_ID"]

    async def main():
        async with TelegramBot(token) as bot:
            print(await bot.get_updates(timeout=0, allowed_updates=["message"]))
            print(await bot.send_message(chat_id_, "test"))

    asyncio.run(main())
