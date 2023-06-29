from __future__ import annotations

from ..errors import SelfBotClientException

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..user import UserClient


class GatewayNotConnected(SelfBotClientException):

    def __init__(self, user: UserClient):  # pyright: ignore
        super().__init__(f"{user} does not have a gateway connection")