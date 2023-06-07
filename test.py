from SelfBotClient import Client, ChannelType


tokens = ["TOKENS"]

selfclient = Client(api_version=10)
selfclient.login(token=tokens)


async def main():

    for user in selfclient.users:
        await user.create_channel(
            guild_id=983442350963576863,
            name="selfclient",
            channel_type=ChannelType.TEXT_CHANNEL
        )


if __name__ == "__main__":
    selfclient.loop.run_until_complete(main())
