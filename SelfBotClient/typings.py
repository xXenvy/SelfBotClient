from typing import Literal, TypedDict
from aiohttp import ClientSession


SESSION = ClientSession
METHOD = Literal["GET", "POST", "DELETE", "PATCH"]
API_VERSION = Literal[9, 10]

AUTH_HEADER = TypedDict("AUTH_HEADER", {"authorization": str})