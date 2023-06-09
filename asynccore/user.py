from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional
from urllib.parse import quote
from logging import getLogger

from asyncio import AbstractEventLoop, sleep
from aiohttp import ClientResponse

from .typings import AUTH_HEADER, RGB_COLOR, MESSAGE_REFERENCE
from .logger import Logger
from .enums import ChannelType

from .permissionbuilder import PermissionBuilder
from .errors import MessagesLimitException
from .cache import Cache

if TYPE_CHECKING:
    from .gateway.gateway import GatewayConnection
    from .http import CustomSession


class UserClient:
    """
    :class:`UserClient` Is the class responsible for the user account.

    :param data: Dict with account data - such as token, name, id.
    :param session: Session to send requests in methods
    """

    def __init__(self, data: dict, session: CustomSession):
        self.data: dict = data

        self._session: CustomSession = session
        self._logger: Logger = getLogger("Logger")  # pyright: ignore
        self._endpoint: str = self.data["endpoint"]
        self._endpoint_gateway: str = self.data["endpoint_gateway"]

        self._members_data: list[Optional[dict]] = []
        self._members_end: bool = True

        self.token: str = self.data["token"]
        self.name: str = self.data["username"]
        self.discriminator: str = f"#{self.data['discriminator']}"
        self.id: int = self.data["id"]

        self._auth_header: AUTH_HEADER = AUTH_HEADER(
            authorization=self.token
        )

        self.loop: AbstractEventLoop = data["loop"]
        self.cache: Cache = Cache(user=self, session=session, endpoint=self._endpoint)
        self.gateway_connection: Optional[GatewayConnection] = None

    def __repr__(self):
        return f"<UserClient(name={self.name}, discriminator={self.discriminator}, id={self.id})>"

    async def reply_message(self, channel_id: int, message_id: int,
                            message_content: str, mention_author: bool = True) -> ClientResponse:

        """
        The reply_message function is used to reply to a message in a channel.

        :param channel_id: Specify the channel to send the message in
        :param message_id: message id of the message that you want to reply to
        :param message_content: A message content
        :param mention_author: Determine whether or not to mention the author of the message
        """

        _url = self._endpoint + f"channels/{channel_id}/messages"

        if self._logger._status:
            self._logger.debug(f"Sending request: POST -> {_url}")

        message_reference = MESSAGE_REFERENCE(
            message_id=message_id,
            channel_id=channel_id
        )

        payload: dict = {
            "content": message_content,
            "message_reference": message_reference
        }

        if not mention_author:
            _message_response: ClientResponse = await self.get_message(channel_id, message_id)
            if _message_response.status == 200:
                _message_data: list[dict] = await _message_response.json()  # pyright: ignore
                _message_data: dict = _message_data[0]
                _message_author_id: int = _message_data["author"]["id"]

                payload["allowed_mentions"] = {
                    "users": [f"{_message_author_id}"]
                }

            else:
                payload["allowed_mentions"] = {
                    "parse": ["users"]
                }

        response: ClientResponse = await self._session.request(
            method="POST", url=_url, headers=self._auth_header, json=payload)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.warning(
                f"Request POST channels/{channel_id}/messages failed.\n -> {self} {await response.json()}")

        return response

    async def send_message(self, channel_id: int, message_content: str) -> ClientResponse:

        """
        The send_message function sends a message to the specified channel.

        :param channel_id: Specify the channel to send the message to
        :param message_content: content of the message
        """

        _url = self._endpoint + f"channels/{channel_id}/messages"

        if self._logger._status:
            self._logger.debug(f"Sending request: POST -> {_url}")

        payload: dict = {
            "content": message_content
        }

        response: ClientResponse = await self._session.request(
            method="POST", url=_url, headers=self._auth_header, json=payload)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.warning(
                f"Request POST channels/{channel_id}/messages failed.\n -> {self} {await response.json()}")

        return response

    async def edit_message(self, channel_id: int, message_id: int, message_content: str) -> ClientResponse:
        """
        The edit_message function allows you to edit a message.

        :param channel_id: Specify the channel id of the message you want to edit
        :param message_id: id the message to edit
        :param message_content: Edit the message content
        """

        _url = self._endpoint + f"/channels/{channel_id}/messages/{message_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: PATCH -> {_url}")

        payload: dict = {
            "content": message_content
        }

        response: ClientResponse = await self._session.request(
            method="PATCH", url=_url, headers=self._auth_header, json=payload)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request PATCH /channels/{channel_id}/messages/{message_id} failed."
                f"\n -> {self} {await response.json()}")

        return response

    async def get_message(self, channel_id: int, message_id: int) -> ClientResponse:
        """
        The get_message function is used to get a message from a channel.

        :param channel_id: Specify the channel id of the message you want to get
        :param message_id: Get the message around that id
        """

        # Since the normal get_message endpoint returns the message
        # "Only bots can use this endpoint" we get the message in a different way

        _url = self._endpoint + f"channels/{channel_id}/messages?limit=1&around={message_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET channels/{channel_id}/messages?limit=1&around={message_id} failed."
                f"\n -> {self} {await response.json()}")

        return response

    async def get_messages(self, channel_id: int, limit: int = 100) -> ClientResponse:
        """
        The get_messages function is used to retrieve a list of message objects from the channel.

        :param channel_id: Specify which channel to get the messages from
        :param limit: Limit the number of messages returned
        """
        if limit > 100:
            raise MessagesLimitException(
                "Unfortunately, but discord only allows a maximum of 100 recent messages to be returned. "
                f"You specified limit={limit}")

        if limit < 2:
            raise MessagesLimitException("Message limit must be greater than 1")

        _url = self._endpoint + f"channels/{channel_id}/messages?limit={limit}"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET channels/{channel_id}/messages failed.\n -> {self} {response.status}")

        return response

    async def delete_message(self, channel_id: int, message_id: int) -> ClientResponse:
        """
        The delete_message function deletes a message from the specified channel.

        :param channel_id: Specify the channel id of the message to be deleted
        :param message_id: Identify the message that is to be deleted
        """

        _url = self._endpoint + f"channels/{channel_id}/messages/{message_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request DELETE channels/{channel_id}/messages/{message_id} failed."
                f"\n -> {self} {await response.json()}")

        return response

    async def delete_channel(self, channel_id: int) -> ClientResponse:
        """
        The delete_channel function deletes a channel from the server.

        :param channel_id: Specify the channel that is to be deleted
        """

        _url = self._endpoint + f"channels/{channel_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request DELETE channels/{channel_id} failed.\n -> {self} {await response.json()}")

        return response

    async def create_channel(self, guild_id: int, name: str, channel_type: ChannelType,
                             topic: Optional[str] = None, user_limit: Optional[int] = None,
                             position: Optional[int] = None, nsfw: Optional[bool] = False) -> ClientResponse:
        """
        The create_channel function creates a channel in the specified guild.

        :param guild_id: Specify the guild id of the server you want to create a channel in
        :param name: Specify the name of the channel
        :param channel_type: Specify what type of channel you want to create
        :param topic: Set the topic of the channel
        :param user_limit: Set the maximum number of users allowed in a voice channel
        :param position: Set the position of the channel in the list
        :param nsfw: Determine whether the channel is nsfw or not
        """

        _url = self._endpoint + f"guilds/{guild_id}/channels"

        if self._logger._status:
            self._logger.debug(f"Sending request: POST -> {_url}")

        payload: dict = {
            "name": name,
            "type": channel_type.value,
            "topic": topic,
            "user_limit": user_limit,
            "position": position,
            "nsfw": nsfw
        }

        response: ClientResponse = await self._session.request(
            method="POST", url=_url, headers=self._auth_header, json=payload)

        if response.status not in (201, 429) and self._logger._status:
            self._logger.error(
                f"Request POST /guilds/{guild_id}/channels failed.\n -> {self} {await response.json()}")

        return response

    async def get_channels(self, guild_id: int) -> ClientResponse:
        """
        The get_channels function is a coroutine that takes in a guild_id and returns an ClientResponse object.
        The function can return the data of all channels on the server

        :param guild_id: Specify the guild id of the server you want to get channels from
        """

        _url = self._endpoint + f"guilds/{guild_id}/channels"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/channels failed.\n -> {self} {await response.json()}.")

        return response

    async def get_channel(self, channel_id: int) -> ClientResponse:
        """
        The get_channel function returns a channel data for the given channel ID.

        :param channel_id: Specify the channel id of the channel you want to get
        """

        _url = self._endpoint + f"/channels/{channel_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET /channels/{channel_id} failed.\n -> {self} {await response.json()}.")

        return response

    async def create_role(self,
                          guild_id: int,
                          name: str,
                          color: Optional[RGB_COLOR] = None,
                          hoist: Optional[bool] = False,
                          permissions: Union[PermissionBuilder, int, None] = None) -> ClientResponse:

        """
        The create_role function creates a role in the specified guild.

        :param guild_id: Specify the guild in which you want to create a role
        :param name: Set the name of the role
        :param color: Set the color of the role
        :param hoist: Determine whether the role should be displayed separately in the user list
        :param permissions: Set the permissions for the role
        """

        _url = self._endpoint + f"guilds/{guild_id}/roles"

        if self._logger._status:
            self._logger.debug(f"Sending request: POST -> {_url}")

        if color:
            r, g, b = color.values()
            _color = (r << 16) + (g << 8) + b  # pyright: ignore
        else:
            _color: int = 0  # pyright: ignore

        if not permissions:
            _permissions: int = 0
        else:
            _permissions: int = permissions.value  # pyright: ignore

        json: dict = {
            "name": name,
            "hoist": hoist,
            "color": _color,
            "permissions": _permissions
        }

        response: ClientResponse = await self._session.request(
            method="POST", url=_url, headers=self._auth_header, json=json)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request POST guilds/{guild_id}/roles failed.\n -> {self} {await response.json()}")

        return response

    async def get_roles(self, guild_id: int) -> ClientResponse:
        """
        get_roles returns a list of data with all the roles on the server

        :param guild_id: Specify the guild id of the server you want to get roles from
        """

        _url = self._endpoint + f"guilds/{guild_id}/roles"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/roles failed.\n -> {self} {await response.json()}")

        return response

    async def delete_role(self, guild_id: int, role_id: int) -> ClientResponse:
        """
        The delete_role function deletes a role from the guild.

        :param guild_id: Specify the guild that you want to delete a role from
        :param role_id: Specify the role_id to be deleted
        """

        _url = self._endpoint + f"guilds/{guild_id}/roles/{role_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request DELETE guilds/{guild_id}/roles/{role_id} failed.\n -> {self} {await response.json()}")

        return response

    async def get_guild_bans(self, guild_id: int) -> ClientResponse:
        """
        The get_guild_bans function returns a list of banned users in the guild.

        :param guild_id: Specify the guild id of the server you want to get banned users from

        """
        _url = self._endpoint + f"guilds/{guild_id}/bans"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/bans failed.\n -> {self} {await response.json()}")

        return response

    async def unban_member(self, guild_id: int, user_id: int) -> ClientResponse:
        """
        The unban_member function unban a user from the guild.

        :param guild_id: Specify the guild that you want to unban a member from
        :param user_id: Specify the user id of the member to unban
        """

        _url = self._endpoint + f"guilds/{guild_id}/bans/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request DELETE guilds/{guild_id}/bans/{user_id} failed.\n -> {self} {await response.json()}")

        return response

    async def ban_member(self, guild_id: int, user_id: int) -> ClientResponse:
        """
        The ban_member function is used to ban a member from the guild.

        :param guild_id: Specify the guild that you want to ban a user from
        :param user_id: Specify the user that is to be banned
        """

        _url = self._endpoint + f"guilds/{guild_id}/bans/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: PUT -> {_url}")

        response: ClientResponse = await self._session.request(
            method="PUT", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request PUT guilds/{guild_id}/bans/{user_id} failed.\n -> {self} {await response.json()}")

        return response

    async def kick_member(self, guild_id: int, user_id: int) -> ClientResponse:
        """
        The kick_member function kicks a member from the guild.

        :param guild_id: Specify the guild that you want to kick a user from
        :param user_id: Identify the user to be kicked
        """

        _url = self._endpoint + f"guilds/{guild_id}/members/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request DELETE guilds/{guild_id}/members/{user_id} failed.\n -> {self} {await response.json()}")

        return response

    async def get_member(self, guild_id: int, user_id: int) -> ClientResponse:
        """
        The get_member function is used to get a member from the guild.

        :param guild_id: Specify the guild that you want to get a member from
        :param user_id: Specify the user id of the member you want to get
        """

        _url = self._endpoint + f"guilds/{guild_id}/members/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/members/{user_id} failed.\n -> {self} {await response.json()}")

        return response

    async def edit_member(self, guild_id: int, user_id: int,
                          nickname: Optional[str] = None,
                          add_roles: Optional[list[int]] = None,
                          remove_roles: Optional[list[int]] = None) -> ClientResponse:

        """
        The edit_member function allows you to edit a member of a guild.

        :param guild_id: Specify the guild that you want to edit a member in
        :param user_id: Specify the user that you want to edit
        :param nickname: Change the nickname of a user in a guild
        :param add_roles: Add roles to a user
        :param remove_roles: Remove roles from a user
        """

        json: dict = {}

        if add_roles or remove_roles:
            user_response: ClientResponse = await self.get_member(guild_id, user_id)
            user_data: dict = await user_response.json()

            roles: Union[None, list[str]] = user_data.get("roles")

            roles_list: list[str] = [] if not roles else roles

            if add_roles:
                for _role in add_roles:
                    roles_list.append(str(_role))

            if remove_roles:
                for _role in remove_roles:
                    try:
                        roles_list.remove(str(_role))
                    except ValueError:
                        pass
            json["roles"] = roles

        if nickname:
            json["nick"] = nickname

        _url = self._endpoint + f"guilds/{guild_id}/members/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: PATCH -> {_url}")

        response: ClientResponse = await self._session.request(
            method="PATCH", url=_url, headers=self._auth_header, json=json)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request PATCH guilds/{guild_id}/members/{user_id} failed.\n -> {self} {await response.json()}")

        return response

    async def add_reaction(self, channel_id: int, message_id: int, emoji: str) -> ClientResponse:
        """
        The add_reaction function adds a reaction to the message with the given ID in the channel with
        the given ID. The emoji parameter is a string that must be an emoticon. Example: \N{FIRE}

        :param channel_id: Specify which channel_id the message is in
        :param message_id: Message ID that you want to add a reaction to
        :param emoji: A reaction to add to the message
        """

        emoji = quote(emoji)

        _url = self._endpoint + f"channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"

        if self._logger._status:
            self._logger.debug(f"Sending request: PUT -> {_url}")

        response: ClientResponse = await self._session.request(
            method="PUT", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request PUT channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me failed."
                f"\n -> {self} {await response.json()}")

        return response

    async def get_reactions(self, channel_id: int, message_id: int, emoji: str) -> ClientResponse:
        """
        The get_reactions function returns a ClientResponse with
        list of users that reacted with the specified emoji.

        :param channel_id: Identify the channel that contains the message
        :param message_id: Identify the message that is being reacted to
        :param emoji: Specify the emoji to get reactions for
        """

        emoji = quote(emoji)

        _url = self._endpoint + f"channels/{channel_id}/messages/{message_id}/reactions/{emoji}"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET channels/{channel_id}/messages/{message_id}/reactions/{emoji}/ failed."
                f"\n -> {self} {await response.json()}")

        return response

    async def delete_reaction(self, channel_id: int, message_id: int, user_id: int, emoji: str) -> ClientResponse:
        """
        The delete_reaction function is used to delete a reaction from a message.

        :param channel_id: Specify the channel where the message is located
        :param message_id: Identify the message that you want to delete a reaction from
        :param user_id: Specify the user whose reaction is to be deleted
        :param emoji: Specify the emoji to be deleted
        """

        emoji = quote(emoji)

        _url = self._endpoint + f"channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request DELETE channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id} failed."
                f"\n -> {self} {await response.json()}")

        return response

    async def get_guild_invites(self, guild_id: int) -> ClientResponse:
        """
        The get_guild_invites function returns a list of invite objects. Requires the 'MANAGE_GUILD' permission.

        :param guild_id: Get the invites for a specific guild
        """

        _url = self._endpoint + f"guilds/{guild_id}/invites"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/invites failed.\n -> {self} {await response.json()}")
        return response

    async def get_guild(self, guild_id: int) -> ClientResponse:
        """
        The get_guild function is used to get information about a guild.

        :param guild_id: Specify the id of the guild you want to get information about
        """

        _url = self._endpoint + f"guilds/{guild_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/invites failed.\n -> {self} {await response.json()}")

        else:
            self.cache.add_guild_to_cache(await response.json())

        return response

    async def send_dm_message(self, user_id: int, message_content: str) -> Optional[ClientResponse]:
        """
        The send_dm_message function sends a direct message to the user with the given user_id.

        :param user_id: Specify the user id of the recipient
        :param message_content: Specify message content
        """

        _url = self._endpoint + "users/@me/channels"

        if self._logger._status:
            self._logger.debug(f"Sending request: POST -> {_url}")

        payload: dict = {
            "recipient_id": user_id
        }

        response: ClientResponse = await self._session.request(
            method="POST", url=_url, headers=self._auth_header, json=payload)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request POST users/@me/channels failed.\n -> {self} {await response.json()}")

        if not response:
            return response

        dm_data: dict = await response.json()
        dm_channel_id: int = dm_data["id"]

        response: ClientResponse = await self.send_message(
            channel_id=dm_channel_id,
            message_content=message_content
        )

        return response

    async def __send_members_requests(self, guild_id: int, channel_id: int, limit: Optional[int]):
        """
        The send_members_requests function is a function that sends requests to the gateway for members.
        This function is used in the get_guild_members wrapper, and it's purpose is to send multiple requests at once.
        The reason why this function exists, and why it's not just part of get_guild_members wrapper,
        is because we want to be able to use this functionality elsewhere.

        :param guild_id: Get the guild id
        :param channel_id: Specify the channel id of the guild
        :param limit: Limit the amount of members that are requested
        """

        index: int = 0

        while self._members_end:
            index += 1

            ranges_list: list = []
            for _ in range(1, 4):
                multiply = index + _

                min_req: int = multiply * 100
                max_req: int = (min_req + 99) - 200
                min_req -= 200

                ranges_list.append([min_req, max_req])

            gateway_payload: dict = {
                "op": 14,
                "d": {
                    "guild_id": guild_id,
                    "typing": True,
                    "threads": False,
                    "activites": True,
                    "channels": {channel_id: ranges_list}
                }
            }
            if not self.gateway_connection:
                from .gateway.errors import GatewayNotConnected
                raise GatewayNotConnected(f"{self} does not have a gateway connection. "
                                          f"This function only works if you run the gateway.")

            gateway: GatewayConnection = self.gateway_connection

            await gateway.application_update_request(request=gateway_payload,
                                                     func=self._get_guild_members_wrapper, limit=limit)
            await sleep(0.6)

    async def get_guild_members(self, guild_id: int, channel_id: int, limit: Optional[int] = None) \
            -> list[Optional[dict]]:
        """
        This function doesn't quite work the same as the others.
        It uses a non-official request through the gateway by which the result may not be complete.

        :param guild_id: Specify the guild_id
        :param channel_id: Specify the channel from which I should fetch members
        :param limit: Provide limit of members

        # Thanks to https://arandomnewaccount.gitlab.io/discord-unofficial-docs/lazy_guilds.html
        """

        self.loop.create_task(self.__send_members_requests(guild_id, channel_id, limit))

        data = []

        self._members_end = True

        while self._members_end:
            await sleep(1)

        data = self._members_data
        self._members_data = []
        self._members_end = False

        return data[0:limit] if limit else data

    async def _get_guild_members_wrapper(self, resp_data: dict, limit: Optional[int]) -> None:
        data: list[dict] = resp_data["ops"]
        members_data: list[Optional[dict]] = []

        for items_data in data:
            if not items_data["items"]:
                self._members_end = False
            for member_data in items_data["items"]:
                if member_data.get("member"):
                    user: dict = member_data["member"]["user"]
                    if user not in members_data:
                        members_data.append(user)

        if not self._members_data:
            self._members_data = members_data
        else:
            self._members_data += members_data

        if self._logger._status and self._members_end:
            self._logger.debug(f"Fetched {len(self._members_data)} members.")

        if limit and len(self._members_data) >= limit:
            self._members_end = False
