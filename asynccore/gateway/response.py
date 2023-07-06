from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from json import loads

if TYPE_CHECKING:
    from ..user import UserClient


class GatewayResponse:
    """
    The class that formats the raw discord response.

    :param data: Store the raw data from discord
    :param user: Pass the user object to the response

    :ivar user: The object of the user who received the response.
    :vartype user: :class:`asynccore.user.UserClient`
    
    :ivar event: Is the response an event
    :vartype event: :class:`bool`

    :ivar op: Op of discord response
    :vartype op: :class:`int`

    :ivar data: Response data
    :vartype data: :class:`dict`

    :ivar sequence: Discord sequence
    :vartype sequence: :class:`int`
    """

    def __init__(self, data: str, user: UserClient):

        self.user: UserClient = user
        self.data: dict = self.format_data(data)
        self.event: bool = False

        self.op: int = self.data["op"]  # pylint: disable=invalid-name

        if self.op == 0:
            self.event: bool = True

        self.sequence: Optional[int] = self.data.get("s")

        if self.data.get("t"):
            self.event_name: str = self.data["t"]
        else:
            self.event_name: str = ""

        self.data: dict = self.data["d"]

    @staticmethod
    def format_data(data: str) -> dict:
        """
        The format_data function takes a string of data and returns a dictionary.

        :param data: Pass in the data that is being formatted
        """
        return loads(data)

    def __repr__(self):
        if self.event:
            return f"<GatewayResponse(user={self.user},event_type={self.event_name}, " \
                 f"op={self.op}, " f"sequence={self.sequence}, data={self.data})>"

        return f"<GatewayResponse(user={self.user}, op={self.op}, " \
               f"sequence={self.sequence}, data={self.data})>"
