from SelfBotClient import Client, user, ClientResponse


tokens = ["TOKEN_1", "TOKEN_2"]

selfclient = Client(api_version=10)
selfclient.login(token=tokens)


async def spam_messages(times=100):
    times = int(times / len(selfclient.users))

    """
    We perform the method .send_message 100 times * number of selfbots. 
    We want to send a total of 100 messages, not 100 * number of selfbots In this case, it will be 50 messages for one selfbot
    """

    for _ in range(times):
        async for response in selfclient.send_message(channel_id=1116069284263776407, message_content="test"):
            data: dict = await response.json()
            message_id: int = data.get("id")
            message_author: dict = data.get("author")


async def spam_messages_one_selfbot(times=100):
    if len(selfclient.users):
        for _ in range(times):

            # We take the first selfbot from the list
            selfbot_1: User = selfclient.users[0]

            # We execute the .send_message method with only one selfbot
            response: ClientResponse = await selfbot_1.send_message(
                                    channel_id=1116069284263776407,
                                    message_content="test")

            data: dict = await response.json()
            message_id: int = data.get("id")
            message_author: dict = data.get("author")


async def main():
    await spam_messages()
    await spam_messages_one_selfbot()


if __name__ == "__main__":
    selfclient.run_async(main())
