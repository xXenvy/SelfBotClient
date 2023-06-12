from SelfBotClient import Client, UserClient, ClientResponse

tokens = ["TOKEN_1", "TOKEN_2"]

client = Client(api_version=10, use_threading=True) # Since this is in beta, you must enable this option yourself.
client.login(token=tokens)


async def spam_messages(channel_id: int, message_content: str, times: int) -> None:

    for _ in range(times):
        async for response in client.send_message(channel_id=channel_id,
                                                  message_content=message_content):
            message_data: dict = await response.json()
            message_id: int = message_data.get("id")
            pass


if __name__ == "__main__":
    # add Tasks to the main Thread and then run it
    func = spam_messages

    client.thread.add_task(func=func(channel_id=123, message_content="test", times=100), name="spam_1")
    client.thread.add_task(func=func(channel_id=123, message_content="test", times=100), name="spam_2")
    client.thread.add_task(func=func(channel_id=123, message_content="test", times=100), name="spam_2")

    client.thread.run() # At this point, we run 3 tasks simultaneously. Which allows us to send 3 messages at once.
