from typing import Optional

from pydantic import BaseModel


class Chat(BaseModel):
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


class User(BaseModel):
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


class Message(BaseModel):
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
    text: Optional[str] = None


class Update(BaseModel):
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
