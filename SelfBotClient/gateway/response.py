from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..user import UserClient

from json import dumps, loads


class GatewayResponse:

    def __init__(self, data: str, user: UserClient):
        self.user: UserClient = user
        self.data: dict = self.format_data(data)
        self.event: bool = False

        self.op: int = self.data["op"]

        if self.op == 0:
            self.event: bool = True

        self.sequence: Optional[int] = self.data.get("s")

        if self.data.get("t"):
            self.event_name: str = self.data.get("t")  # pyright: ignore
        else:
            self.event_name: str = ""

        self.data: dict = self.data["d"]

    def format_data(self, data: str) -> dict:
        return loads(data)

    def __repr__(self):
        return f"<GatewayResponse(user={self.user},event_type={self.event_name}, " \
               f"op={self.op}, " f"sequence={self.sequence}, data={self.data})>"
