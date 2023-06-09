from SelfBotClient import Client, ClientResponse, ChannelType
from threading import Thread


def get_tokens() -> list[str]:
    with open("tokens.txt", mode="r") as file:
        _tokens: str = file.read()

    return _tokens.split("\n")


selfclient = Client(api_version=10, request_latency=0.0, ratelimit_additional_cooldown=0.0)
selfclient.login(token=get_tokens())


async def spam_message():
    for _ in range(10):
        async for response in selfclient.send_message(
            channel_id=1116783500851429517,
            message_content="@everyone\n:clown:"
        ):
            if response.status != 200:
                print(await response.json())


