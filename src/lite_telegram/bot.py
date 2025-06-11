import logging
from contextlib import suppress
from json import JSONDecodeError
from typing import Any, Iterable, Type, TypeVar

from httpx import AsyncClient, HTTPError, Response
from loguru import logger
from pydantic import BaseModel, ValidationError
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential

from lite_telegram.exceptions import TelegramException
from lite_telegram.models import Message, Update
from lite_telegram.utils import LoguruTenacityAdapter

T = TypeVar("T", bound=BaseModel)

BASE_URL_TEMPLATE = "https://api.telegram.org/bot{token}/"


class TelegramBot:
    def __init__(self, client: AsyncClient, token: str, timeout: int = 60) -> None:
        self.client = client
        self.__token = token
        self.timeout = timeout

        self.__base_url = BASE_URL_TEMPLATE.format(token=self.__token)
        self._offset = 0

    async def get_me(self) -> dict | list[dict]:
        return await self._request(endpoint="getMe")

    async def send_message(self, chat_id: int, text: str) -> Message:
        endpoint = "sendMessage"
        data = {"chat_id": chat_id, "text": text}

        logger.info("Sending message to {}: '{}'.", chat_id, text)
        json_data = await self._request(endpoint=endpoint, data=data)
        return self._validate_model(json_data, Message)

    async def get_updates(
        self, timeout: int = 300, allowed_updates: list[str] | None = None
    ) -> list[Update]:
        endpoint = "getUpdates"
        data = {"timeout": timeout, "offset": self._offset}
        if allowed_updates is not None:
            data["allowed_updates"] = allowed_updates
        request_timeout = self.timeout + timeout

        json_data = await self._request(endpoint=endpoint, data=data, timeout=request_timeout)
        updates = [self._validate_model(data, Update) for data in json_data]
        self._update_offset(updates)
        return updates

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2),
        before_sleep=before_sleep_log(LoguruTenacityAdapter(logger), logging.WARNING),
        reraise=True,
    )
    async def _request(
        self, endpoint: str, data: dict[str, Any] | None = None, timeout: int | None = None
    ) -> dict | list[dict]:
        method = "POST"
        url = self.__base_url + endpoint
        timeout = timeout if timeout is not None else self.timeout
        self._log_request(method, url, data, timeout)

        try:
            response = await self.client.request(method, url, data=data, timeout=timeout)
        except HTTPError as exc:
            raise TelegramException("Request to telegram api failed.") from exc

        self._check_response(response)
        return self._parse_response(response)

    def _log_request(self, method: str, url: str, data: dict | None, timeout: int) -> None:
        logger.debug(
            "Sending request to telegram: method - '{}', url - '{}', timeout - '{}'.",
            method,
            url.replace(self.__token, "********"),
            timeout,
        )
        if data is not None:
            logger.debug("Request data: '{}'.", data)

    @staticmethod
    def _check_response(response: Response) -> None:
        if not response.is_success:
            logger.error("Error status code {}.", response.status_code)
            with suppress(Exception):
                if error_text := response.text:
                    logger.error("Response data: '{}'.", error_text)
            raise TelegramException("Received failed response")

    @staticmethod
    def _parse_response(response: Response) -> dict | list[dict]:
        try:
            data = response.json()
        except (TypeError, JSONDecodeError) as exc:
            raise TelegramException(exc) from exc

        if (
            isinstance(data, dict)
            and data.get("ok")
            and isinstance((result := data.get("result")), (list, dict))
        ):
            return result

        raise TelegramException(f"Incorrect response format: {data}.")

    @staticmethod
    def _validate_model(data: dict | list[dict], model: Type[T]) -> T:
        try:
            return model.model_validate(data)
        except ValidationError as exc:
            raise TelegramException(exc) from exc

    def _update_offset(self, updates: Iterable) -> None:
        self._offset = max((update.update_id + 1 for update in updates), default=self._offset)
