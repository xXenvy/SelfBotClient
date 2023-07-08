from asynccore import Client, UserClient, ClientResponse

tokens = ["TOKEN_1", "TOKEN_2"]

client = Client(api_version=10)
client.login(tokens=tokens)


async def spam_messages(channel_id: int, message_content: str, times: int) -> None:
    """
    methods used by `.client` call it in all selfbots.
    This means that a loop executed 100 times will send a message 100 * number of selfbots.
    If we want 100 messages then we have to divide the number by the number of selfbots.

    -> Or use the method which is defined below.
    """
    times: int = int(times / len(client.users))

    for _ in range(times):
        async for response in client.send_message(channel_id=channel_id,
                                                  message_content=message_content):
            message_data: dict = await response.json()
            message_id: int = message_data.get("id")
            # do something


async def spam_messages_one_selfbot(channel_id: int, message_content: str, times: int) -> None:
    # We take the first selfbot from the list of saved ones.
    self_bot_1: UserClient = client.users[0]

    for _ in range(times):
        response: ClientResponse = await self_bot_1.send_message(channel_id=channel_id,
                                                                 message_content=message_content)

        message_data: dict = await response.json()
        message_id: int = message_data.get("id")

        # This way we will send 100 messages using one selfbot


async def main():

    await spam_messages(channel_id=123, message_content="hi!", times=100)
    await spam_messages_one_selfbot(channel_id=123, message_content="hi! one selfbot!", times=100)


if __name__ == "__main__":
    "I recommend that you run asynchrochrochine methods this way."
    "I'm not sure how asyncio.run(func), for example, will behave."

    client.run_async(main())
