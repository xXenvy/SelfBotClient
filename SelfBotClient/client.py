from .http import HTTPClient
from .typings import API_VERSION, ClientResponse, RGB_COLOR
from .enums import ChannelType
from .permissionbuilder import PermissionBuilder
from .tasks import Tasks
from .user import UserClient

from collections.abc import AsyncIterable

from typing import Union, Optional
from asyncio import AbstractEventLoop
from threading import Thread
from time import sleep


class Client(HTTPClient):
    """
    :class:`Client` supports all services of the :class:`SelfBotClient.user`.
    It has methods such as :class:`Client.send_message` which it calls in all users.

    :param api_version: version of the discord api used by the client
    :param loop: Set the event loop that will be used by the client
    :param logger: Enable/disable the logger
    :param request_latency: Control the rate of requests sent to discord
    :param ratelimit_additional_cooldown: Add a cooldown to the ratelimit
    :param use_tasks: Enable or disable the tasks option (:class:`SelfBotClient.tasks`), which for now is in beta.

    """

    __version__: str = "1.1.2"

    def __init__(
            self,
            api_version: API_VERSION,
            loop: Union[AbstractEventLoop, None] = None,
            logger: bool = True,
            request_latency: float = 0.1,
            ratelimit_additional_cooldown: float = 10,
            use_threading: bool = False
    ):  # type: ignore

        super().__init__(api_version, loop, logger, request_latency, ratelimit_additional_cooldown, self)

        if use_threading:
            self.tasks: Tasks = Tasks(client=self)

    def login(self, tokens: Union[str, list[str]]) -> None:
        """
        The login function is used to check the provided tokens.

        :param tokens: tokens to check
        """

        if self.logger._status:  # pyright: ignore
            self.logger.info("Checking the provided tokens")

        self._check_tokens(tokens)

    async def send_message(self, channel_id: int, message_content: str) -> Optional[AsyncIterable[ClientResponse]]:
        """
        The send_message function sends a message to the specified channel.

        :param channel_id: Specify the channel to send the message to
        :param message_content: content of the message
        """

        for user in self.users:
            response: ClientResponse = await user.send_message(channel_id, message_content)
            yield response

    async def delete_channel(self, channel_id: int) -> Union[None, ClientResponse]:
        """
        The delete_channel function deletes a channel from the server.

        :param channel_id: Specify the channel that is to be deleted
        """

        for user in self.users:
            response: ClientResponse = await user.delete_channel(channel_id)
            if response.status == 200:
                return response

    async def delete_channels(self, channel_ids: list[int]) -> Optional[AsyncIterable[ClientResponse]]:
        """
        The delete_channels function takes a list of channel_ids and deletes them.
        It returns an AsyncIterable of ClientResponse objects, which can be used to check the status code for each request.

        :param channel_ids: Specify the list of channel ids that will be deleted
        """

        while len(channel_ids):
            for user in self.users:
                channel_id: int = channel_ids.pop(0)
                response: ClientResponse = await user.delete_channel(channel_id)
                yield response

    async def create_channel(self, guild_id: int, name: str, channel_type: ChannelType,
                             topic: Optional[str] = None, user_limit: Optional[int] = None,
                             position: Optional[int] = None, nsfw: Optional[bool] = False) -> Optional[AsyncIterable[ClientResponse]]:
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

        for user in self.users:
            response: ClientResponse = await user.create_channel(guild_id, name, channel_type, topic, user_limit, position, nsfw)
            yield response

    async def get_channels(self, guild_id: int) -> Optional[AsyncIterable[ClientResponse]]:
        """
        The get_channels function is a coroutine that takes in a guild_id and returns an AsyncIterable of ClientResponse objects.
        The function can return the data of all channels on the server

        :param guild_id: Specify the guild id of the server you want to get channels from
        """

        for user in self.users:
            response: ClientResponse = await user.get_channels(guild_id)
            yield response

    async def create_role(self,
                                guild_id: int,
                                name: str,
                                color: Optional[RGB_COLOR] = None,
                                hoist: Optional[bool] = False,
                                permissions: Optional[PermissionBuilder] = None) -> Optional[AsyncIterable[ClientResponse]]:
        """
        The create_role function creates a role in the specified guild.

        :param guild_id: Specify the guild in which you want to create a role
        :param name: Set the name of the role
        :param color: Set the color of the role
        :param hoist: Determine whether the role should be displayed separately in the user list
        :param permissions: Set the permissions for the role
        """

        for user in self.users:
            response: ClientResponse = await user.create_role(guild_id, name, color, hoist, permissions)
            yield response

    async def get_roles(self, guild_id: int) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        get_roles returns a list of data with all the roles on the server

        :param guild_id: Specify the guild id of the server you want to get roles from
        """
        for user in self.users:
            response: ClientResponse = await user.get_roles(guild_id)
            yield response

    async def delete_roles(self, guild_id: int, role_ids: list[int]) -> Union[None, AsyncIterable[ClientResponse]]:

        """
        delete_roles function removes all roles with id in the list

        :param guild_id: Specify the guild that the roles are being deleted from
        :param role_ids: Specify the roles that are to be deleted
        """

        while len(role_ids):
            for user in self.users:
                role_id: int = role_ids.pop(0)
                response: ClientResponse = await user.delete_role(guild_id, role_id)
                yield response

    async def delete_role(self, guild_id: int, role_id: int) -> Union[None, ClientResponse]:
        """
        The delete_role function deletes a role from the guild.

        :param guild_id: int: Specify the guild that you want to delete a role from
        :param role_id: int: Specify the role_id to be deleted
        """

        for user in self.users:
            response: ClientResponse = await user.delete_role(guild_id, role_id)
            if response.status == 204:
                return response

    async def get_bans(self, guild_id: int) -> Union[None, ClientResponse]:
        """
        The get_bans function returns a list of banned users in the guild.

        :param guild_id: Specify the guild id of the server you want to get banned users from
        """

        for user in self.users:
            response: ClientResponse = await user.get_bans(guild_id)
            if response.status == 200:
                return response

    async def ban_member(self, guild_id: int, user_id: int) -> Union[None, ClientResponse]:
        """
        The ban_member function is used to ban a member from the guild.

        :param guild_id: Specify the guild that you want to ban a user from
        :param user_id: Specify the user that is to be banned
        """

        for user in self.users:
            response: ClientResponse = await user.ban_member(guild_id, user_id)
            if response.status == 204:
                return response

    async def unban_members(self, guild_id: int, user_ids: list[int]) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The unban_members function is a coroutine that takes in a guild_id and user_ids list.
        It then iterates through the users list, popping off the first user id from the
        user_ids list and passing it to unban_member function of each client. If there is no
        response or if there was an error, it will return None. Otherwise, it will yield back
        the response.

        :param guild_id: Specify the guild id of the server you want to unban members from
        :param user_ids: Store the list of user ids to unban
        """

        while len(user_ids):
            for user in self.users:
                user_id: int = user_ids.pop(0)
                response: ClientResponse = await user.unban_member(guild_id, user_id)
                if response.status == 204:
                    yield response

    async def unban_member(self, guild_id: int, user_id: int) -> Union[None, ClientResponse]:
        """
        The unban_member function unban a user from the guild.

        :param guild_id: Specify the guild that you want to unban a member from
        :param user_id: Specify the user id of the member to unban
        """

        for user in self.users:
            response: ClientResponse = await user.unban_member(guild_id, user_id)
            if response.status == 204:
                return response

    async def ban_members(self, guild_id: int, user_ids: list[int]) -> Union[None, AsyncIterable[ClientResponse]]:

        """
        The ban_members function is a coroutine that takes in a guild_id and user_ids list.
        It then iterates through the users list, popping off the first user id from the
        user_ids list and passing it to ban_member function of each client. The response
        from each client is yielded back to whatever called this function.

        :param guild_id: Specify the guild to ban the user from
        :param user_ids: Store the list of user ids that will be banned
        """

        while len(user_ids):
            for user in self.users:
                user_id: int = user_ids.pop(0)
                response: ClientResponse = await user.ban_member(guild_id, user_id)
                yield response

    async def kick_member(self, guild_id: int, user_id: int) -> Union[None, ClientResponse]:
        """
        The kick_member function kicks a member from the guild.

        :param guild_id: Specify the guild that you want to kick a user from
        :param user_id: Identify the user to be kicked
        """
        for user in self.users:
            response: ClientResponse = await user.kick_member(guild_id, user_id)
            if response.status == 204:
                return response

    async def kick_members(self, guild_id: int, user_ids: list[int]) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The kick_members function is a coroutine that takes in a guild_id and user_ids list.
        It then iterates through the users list, popping off the first user id from the
        user_ids list and kicking them from the specified guild. It yields each response as it goes.

        :param guild_id: Specify which guild the user is in
        :param user_ids: list with id of people to kick out
        """

        while len(user_ids):
            for user in self.users:
                user_id: int = user_ids.pop(0)
                response: ClientResponse = await user.kick_member(guild_id, user_id)
                yield response

    async def get_member(self, guild_id: int, user_id: int) -> Union[None, ClientResponse]:
        """
        The get_member function is used to get a member from the guild.

        :param guild_id: Specify the guild that you want to get a member from
        :param user_id: Specify the user id of the member you want to get
        """

        for user in self.users:
            response: ClientResponse = await user.get_member(guild_id, user_id)
            if response.status == 200:
                return response

    async def edit_member(self, guild_id: int, user_id: int,
                                                                nickname: Optional[str] = None,
                                                                add_roles: Optional[list[int]] = None,
                                                                remove_roles: Optional[list[int]] = None) -> Union[None, ClientResponse]:

        """
        The edit_member function allows you to edit a member of a guild.

        :param guild_id: Specify the guild that you want to edit a member in
        :param user_id: Specify the user that you want to edit
        :param nickname: Change the nickname of a user in a guild
        :param add_roles: Add roles to a user
        :param remove_roles: Remove roles from a user
        """

        for user in self.users:
            response: ClientResponse = await user.edit_member(guild_id, user_id, nickname, add_roles, remove_roles)
            if response and response.status == 200:
                return response

    async def add_reaction(self, channel_id: int, message_id: int, emoji: str) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The add_reaction function adds a reaction to the message with the given ID in the channel with
        the given ID. The emoji parameter is a string that must be an emoticon. Example: \N{FIRE}

        :param channel_id: Specify which channel_id the message is in
        :param message_id: Message ID that you want to add a reaction to
        :param emoji: A reaction to add to the message
        """

        for user in self.users:
            response: ClientResponse = await user.add_reaction(channel_id, message_id, emoji)
            yield response

    async def get_reactions(self, channel_id: int, message_id: int, emoji: str) -> Union[None, ClientResponse]:
        """
        The get_reactions function returns a ClientResponse with
        list of users that reacted with the specified emoji.

        :param channel_id: Identify the channel that contains the message
        :param message_id: Identify the message that is being reacted to
        :param emoji: Specify the emoji to get reactions for
        """

        for user in self.users:
            response: ClientResponse = await user.get_reactions(channel_id, message_id, emoji)
            if response.status == 204:
                return response

    async def delete_reaction(self, channel_id: int, message_id: int, user_id: int, emoji: str) -> Union[None, ClientResponse]:
        """
        The delete_reaction function is used to delete a reaction from a message.

        :param channel_id: Specify the channel where the message is located
        :param message_id: Identify the message that you want to delete a reaction from
        :param user_id: Specify the user whose reaction is to be deleted
        :param emoji: Specify the emoji to be deleted
        """

        for user in self.users:
            response: ClientResponse = await user.delete_reaction(channel_id, message_id, user_id, emoji)
            if response.status == 204:
                return response

    async def on_ready(self, user: UserClient) -> None:
        ...

    async def on_message_create(self, user: UserClient, message_data: dict) -> None:
        ...

    async def on_message_delete(self, user: UserClient, message_data: dict) -> None:
        ...

    async def on_message_edit(self, user: UserClient, message_data: dict) -> None:
        ...
