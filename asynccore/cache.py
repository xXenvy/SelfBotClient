from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any

from .typings import AUTH_HEADER

if TYPE_CHECKING:
    from .client import ClientResponse, UserClient
    from .http import CustomSession
    from .user import UserClient
    from .gateway.response import GatewayResponse


class Cache:
    """
    A Cache object is assigned to each :class:`asynccore.user.UserClient` object. It stores servers, channels, messages.
    The startup function acquires all data (except messages) at startup if **startup_cache**
    in class :class:`asynccore.client.Client` is set to True


    :param session: Store the session object that is passed to it
    :param user: Store the user's client
    :param endpoint: Set the endpoint of the api
    """

    def __init__(self, session: CustomSession, user: UserClient, endpoint: str) -> None:
        guild_id = int

        self._endpoint: str = endpoint

        self.session: CustomSession = session
        self.user: UserClient = user

        self.__cached_guilds: list[dict] = []
        self.__cached_channels: dict[guild_id, list[dict[str, Any]]] = {}
        self.__cached_messages: dict[guild_id, list[dict[str, Any]]] = {}

    async def __request_guilds(self):
        url: str = self._endpoint + "users/@me/guilds"

        response: ClientResponse = await self.session.request(
            url=url,
            method="GET",
            headers=AUTH_HEADER(authorization=self.user.token)
        )

        if response.status == 200:
            guilds_data = await response.json()
            for guild in guilds_data:
                if guild["id"] not in self.__cached_guilds:
                    self.__cached_guilds.append(guild)

    async def __request_channels(self):
        for guild_data in self.__cached_guilds:
            guild_id: int = int(guild_data["id"])

            url: str = self._endpoint + f"guilds/{guild_id}/channels"

            response: ClientResponse = await self.session.request(
                url=url,
                method="GET",
                headers=AUTH_HEADER(authorization=self.user.token)
            )

            if response.status == 200:
                if guild_id not in self.__cached_channels.keys():  # pylint: disable=consider-iterating-dictionary
                    channels_data: list[dict] = await response.json()
                    self.__cached_channels[guild_id] = channels_data

    async def __request_messages(self):  # pylint: disable=unused-private-member
        ...

        # Disabled due to long startup time and ratelimit

        # for guild_id, channels in self.cached_channels.items():
        #     for channel_data in channels:
        #         channel_id: int = int(channel_data["id"])
        #         url: str = self._endpoint + f"channels/{channel_id}/messages"
        #
        #         response: ClientResponse = await self.session.request(
        #             url=url,
        #             method="GET",
        #             headers=AUTH_HEADER(authorization=self.user.token)
        #         )
        #
        #         if response.status == 200:
        #             data: list[dict] = await response.json()
        #             if not self.cached_messages.get(guild_id):
        #                 self.cached_messages[guild_id] = [{channel_id: data}]
        #             else:
        #                 messages_data: list[dict] = self.cached_messages.get(guild_id)
        #                 messages_data.append({channel_id: data})

    async def startup_cache(self):
        """
        The startup_cache function is called when the account starts up.
        It checks if there are any cached guilds, and if not, it requests them from Discord.
        Then it requests channels from Discord.

        .. note::
            The function will only get called if the **startup_cache** parameter is set to True
            in the :class:`asynccore.client.Client` class.
        """

        if not self.__cached_guilds:
            await self.__request_guilds()
            await self.__request_channels()

    def get_channel(self, channel_id: int, guild_id: Optional[int] = None) -> Optional[dict]:
        """
        The get_channel function is used to retrieve a channel's data from the cache.

        :param channel_id: Get the channel id of a specific channel
        :param guild_id: Specify the guild id of the channel
        """

        def check(_channel_data: dict) -> bool:
            return int(_channel_data["id"]) == channel_id

        if guild_id:
            channels: Optional[list[dict]] = self.__cached_channels.get(guild_id)
            if not channels:
                return None

            for channel_data in channels:
                if check(channel_data):
                    return channel_data
        else:
            for channels in self.__cached_channels.values():
                for channel_data in channels:
                    if check(channel_data):
                        return channel_data

    def get_channels(self, guild_id: int) -> Optional[list[dict]]:
        """
        The get_channels function returns a list of channels for the given guild_id.
        If no channels are found, it will return None.

        :param guild_id: Get the channels from a specific guild
        """

        channels: Optional[list[dict]] = self.__cached_channels.get(int(guild_id))

        if not channels:
            return None

        return channels

    def get_guild(self, guild_id: int) -> Optional[dict]:
        """
        The get_guild function is used to get a guild's data from the cache.
        It takes in a guild_id and returns the corresponding dictionary of that guild's data.
        If no such dictionary exists, it returns None.

        :param guild_id: Specify the id of the guild you want to get information about
        """

        def check(_guild_data: dict) -> bool:
            return int(_guild_data["id"]) == int(guild_id)

        for guild_data in self.__cached_guilds:
            if check(guild_data):
                return guild_data

    def get_guilds(self) -> list[dict]:
        """
        The get_guilds function returns a list of dictionaries containing the guilds that the account is in.
        The dictionary contains information about each guild, such as its name and ID.
        """

        return self.__cached_guilds

    def get_messages(self, guild_id: int) -> Optional[list[dict]]:
        """
        The get_messages function returns a list of messages from the cache.

        :param guild_id: Get the messages from a specific guild
        """

        messages: Optional[list[dict]] = self.__cached_messages.get(int(guild_id))

        if not messages:
            return None

        return messages

    def get_message(self, guild_id: int, message_id: int) -> Optional[dict]:
        """
        The get_message function is used to retrieve a message from the cache.

        :param guild_id: Specify the guild id of the message
        :param message_id: Find the message in the list of messages
        """

        messages: Optional[list[dict]] = self.__cached_messages.get(int(guild_id))

        if not messages:
            return

        for message in messages:
            if int(message["id"]) == int(message_id):
                return message

    def get_messages_from_channel(self, guild_id: int, channel_id: int) -> Optional[list[Optional[dict]]]:
        """
        The get_messages_from_channel function takes a guild_id and channel_id,
        and returns all messages from the specified channel. If no messages are found,
        it will return None.

        :param guild_id: Get the messages from a specific guild
        :param channel_id: Get the messages from a specific channel
        """

        messages: Optional[list[dict]] = self.__cached_messages.get(int(guild_id))
        sorted_messages: list[Optional[dict]] = []

        if not messages:
            return None

        for message in messages:
            if int(channel_id) == int(message["channel_id"]):
                sorted_messages.append(message)

        if not sorted_messages:
            return None

        return sorted_messages

    def add_channel_to_cache(self, channel_data: dict) -> None:
        """
        The add_channel_to_cache function adds a channel to the cache.

        :param channel_data: Pass the channel data
        """

        guild_id: int = int(channel_data["guild_id"])

        if self.__cached_channels.get(guild_id):
            cached_channels: list = self.__cached_channels[guild_id]
            cached_channels.append(channel_data)
            self.__cached_channels[guild_id] = cached_channels
        else:
            self.__cached_channels[guild_id] = [channel_data]

    def add_message_to_cache(self, message_data: dict) -> None:
        """
        The add_message_to_cache function adds a message to the cache.

        :param message_data: Pass in the message data that is to be added to the cache
        """

        guild_id: int = int(message_data["guild_id"])

        if self.__cached_messages.get(guild_id):
            cached_messages: list = self.__cached_messages[guild_id]
            cached_messages.append(message_data)
            self.__cached_messages[guild_id] = cached_messages
        else:
            self.__cached_messages[guild_id] = [message_data]

    def add_guild_to_cache(self, guild_data: dict) -> None:
        """
        The add_guild_to_cache function adds a guild to the cache.

        :param guild_data: Pass dictionary of guild data
        """

        for guild in self.__cached_guilds:
            if int(guild["id"]) == int(guild_data["id"]):
                return

        self.__cached_guilds.append(guild_data)

    def update_message(self, guild_id: int, message_data: dict) -> None:
        """
        The update_message function is used to update a message in the cache.

        :param guild_id: Specify the guild id of the message
        :param message_data: Updated message data
        """

        guild_id = int(guild_id)  # just to make sure

        messages: Optional[list[dict]] = self.__cached_messages.get(guild_id)

        if not messages:
            self.__cached_messages[guild_id] = [message_data]
            return

        for index, message in enumerate(messages):
            if int(message_data["id"]) == int(message["id"]):
                del messages[index]

        messages.append(message_data)
        self.__cached_messages[guild_id] = messages

    def update_channel(self, guild_id: int, channel_data: dict) -> None:
        """
        The update_channel function is used to update the cached channel for a guild.

        :param guild_id: Pass guild_id
        :param channel_data: Pass the updated channel_data
        """

        guild_id = int(guild_id)  # just to make sure

        channels: Optional[list[dict]] = self.__cached_channels.get(guild_id)
        if not channels:
            self.__cached_channels[guild_id] = [channel_data]
            return

        for index, channel in enumerate(channels):
            if int(channel_data["id"]) == int(channel["id"]):
                del channels[index]

        channels.append(channel_data)
        self.__cached_channels[guild_id] = channels

    def update_guild(self, guild_data: dict) -> None:
        """
        The update_guild function updates the cached guilds list with a new guild data.

        :param guild_data: Pass in the guild data
        """

        guild_id: int = int(guild_data["id"])

        guilds: Optional[list[dict]] = self.__cached_guilds

        if not len(guilds):
            self.__cached_guilds = [guild_data]
            return

        for index, guild in enumerate(guilds):
            if int(guild["id"]) == guild_id:
                del guilds[index]

        guilds.append(guild_data)
        self.__cached_messages[guild_id] = guilds


class CacheEventHandler:
    """
    CacheEventHandler handles the caching of events.
    For example, when the gateway receives a response about a new message this class will add this message to the cache.

    :param response: Store the gatewayresponse object that was passed to the gateway
    :param user: Get the user object who recived response
    """

    def __init__(self, response: GatewayResponse, user: UserClient):
        self.event_name: str = response.event_name
        self.response: GatewayResponse = response
        self.user: UserClient = user

    def handle_cache(self):
        """
        Function checks if the event name is either
        MESSAGE_CREATE or CHANNEL_CREATE, and then adds that data to the cache.
        """

        if self.event_name == "MESSAGE_CREATE":
            self.user.cache.add_message_to_cache(self.response.data)

        if self.event_name == "CHANNEL_CREATE":
            self.user.cache.add_channel_to_cache(self.response.data)

    def get_args(self) -> Optional[tuple]:
        """
        The get_args function is needed to get the arguments to call events like `on_message_edit`
        It gets the **before_data** argument from the cache and then updates the cache
        """

        args: Optional[tuple] = None

        if self.event_name == "MESSAGE_UPDATE":
            guild_id: int = int(self.response.data["guild_id"])
            message_id: int = int(self.response.data["id"])

            before_message: Optional[dict] = self.user.cache.get_message(guild_id, message_id)

            if not before_message:
                before_message = {}

            args = (self.user, before_message, self.response.data)

            self.user.cache.update_message(guild_id, self.response.data)

        if self.event_name == "CHANNEL_UPDATE":
            guild_id: int = int(self.response.data["guild_id"])
            channel_id: int = int(self.response.data["id"])
            before_channel: Optional[dict] = self.user.cache.get_channel(channel_id, guild_id)

            if not before_channel:
                before_channel = {}

            args = (self.user, before_channel, self.response.data)

            self.user.cache.update_channel(guild_id, self.response.data)

        if self.event_name == "GUILD_UPDATE":
            guild_id: int = int(self.response.data["guild_id"])
            before_guild: Optional[dict] = self.user.cache.get_guild(guild_id)

            if not before_guild:
                before_guild = {}

            args = (self.user, before_guild, self.response.data)

            self.user.cache.update_guild(self.response.data)

        return args
