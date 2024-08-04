import typing
from dataclasses import dataclass
from typing import Any, Optional, Union


def _is_optional(obj: Any):
    origin = typing.get_origin(obj)
    args = typing.get_args(obj)
    return origin is Union and len(args) == 2 and type(None) in args


class Model:
    @classmethod
    def from_dict(cls, data: dict) -> "Model":
        kwargs = {}

        for arg, value in data.items():
            if arg in cls.__annotations__:
                hint = cls.__annotations__[arg]

                if _is_optional(hint):
                    args = typing.get_args(hint)
                    hint = args[0]

                if issubclass(hint, Model) and isinstance(value, dict):
                    value = hint.from_dict(value)

                kwargs[arg] = value

        return cls(**kwargs)


@dataclass(frozen=True)
class Chat(Model):
    """This object represents a chat.

    Attributes:
        id: Unique identifier for this chat. This number may have more than 32 significant bits
            and some programming languages may have difficulty/silent defects in interpreting it.
            But it has at most 52 significant bits, so a signed 64-bit integer or double-precision
            float type are safe for storing this identifier.
        type: Type of the chat, can be either "private", "group", "supergroup" or "channel"
    """

    id: int
    type: str


@dataclass(frozen=True)
class User(Model):
    """This object represents a Telegram user or bot.

    Attributes:
        id: Unique identifier for this user or bot. This number may have more than 32 significant
            bits and some programming languages may have difficulty/silent defects in interpreting
            it. But it has at most 52 significant bits, so a 64-bit integer or double-precision
            float type are safe for storing this identifier.
        is_bot: True, if this user is a bot
        first_name: User's or bot's first name
    """

    id: int
    is_bot: bool
    first_name: str


@dataclass(frozen=True)
class Message(Model):
    """This object represents a message.

    Attributes:
        message_id: Unique message identifier inside this chat
        chat: Chat the message belongs to
        from_: (Optional) Sender of the message; empty for messages sent to channels. For backward
            compatibility, the field contains a fake sender user in non-channel chats, if the
            message was sent on behalf of a chat.
        text: (Optional) For text messages, the actual UTF-8 text of the message
    """

    message_id: int
    chat: Chat
    from_: Optional[User] = None
    text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        if "from" in data:
            data["from_"] = data.pop("from")

        return super().from_dict(data)


@dataclass(frozen=True)
class Update(Model):
    """This object represents an incoming update.

    Attributes:
        update_id: The update's unique identifier. Update identifiers start from a certain
            positive number and increase sequentially. This identifier becomes especially handy
            if you're using webhooks, since it allows you to ignore repeated updates or to restore
            the correct update sequence, should they get out of order. If there are no new updates
            for at least a week, then identifier of the next update will be chosen randomly
            instead of sequentially.
        message: (Optional) New incoming message of any kind - text, photo, sticker, etc.
    """

    update_id: int
    message: Optional[Message] = None
