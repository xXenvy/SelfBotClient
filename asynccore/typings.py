from typing import Literal, TypedDict
from aiohttp import ClientResponse  # pylint: disable=unused-import

METHOD = Literal["GET", "POST", "DELETE", "PATCH", "PUT"]
API_VERSION = Literal[9, 10]  # pylint: disable=invalid-name
AUTH_HEADER = TypedDict("AUTH_HEADER", {"authorization": str})
RGB_COLOR = TypedDict("RGB_COLOR", {"R": int, "G": int, "B": int})
MESSAGE_REFERENCE = TypedDict("MESSAGE_REFERENCE", {"message_id": int, "channel_id": int})
