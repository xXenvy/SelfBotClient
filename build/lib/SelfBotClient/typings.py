from typing import Literal, TypedDict, TYPE_CHECKING
from aiohttp import ClientResponse


METHOD = Literal["GET", "POST", "DELETE", "PATCH", "PUT"]
API_VERSION = Literal[9, 10]
AUTH_HEADER = TypedDict("AUTH_HEADER", {"authorization": str})
RGB_COLOR = TypedDict("RGB_COLOR", {"R": int, "G": int, "B": int})