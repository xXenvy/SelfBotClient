from SelfBotClient import Client, ChannelType, \
    ClientResponse, User, AUTH_HEADER, RGB_COLOR, Permissions, PermissionBuilder


tokens = ["MTExNjUwOTUyMTY4NzM2Nzc2Mw.GFZdMn.6v2Bbvk0FAVkxTvSSyqxVhNOvav_tEn4CK0zU0"]

selfclient = Client(api_version=10)
selfclient.login(token=tokens)


async def main():

    async for response in selfclient.kick_member(
                                            guild_id=983442350963576863,
                                            user_id=1043898474019692584):
        print(response.status)


if __name__ == "__main__":
    selfclient.run_async(main())
