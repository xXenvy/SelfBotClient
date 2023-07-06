from __future__ import annotations

from typing import TYPE_CHECKING

from ..errors import SelfBotClientException

if TYPE_CHECKING:
    from ..user import UserClient


class MissingEventName(SelfBotClientException):

    def __init__(self, func: callable):  # pyright: ignore
        super().__init__(f"Missing event_name value in {func}")


class InvalidEventName(SelfBotClientException):

    def __init__(self, name: str):  # pyright: ignore
        super().__init__(f"Event name: {name} is not available.")


class FunctionIsNotCoroutine(SelfBotClientException):

    def __init__(self, function: callable):  # pyright: ignore
        super().__init__(f"Function: {function} is not coroutine.")


class GatewayNotConnected(SelfBotClientException):

    def __init__(self, text: str = None):  # pyright: ignore
        super().__init__(text)
