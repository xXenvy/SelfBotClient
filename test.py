from SelfBotClient import Client, ChannelType, ClientResponse, User, AUTH_HEADER, RGB_COLOR

from typing import Optional


tokens = ["MTA4ODE1MTM1ODg1MjU2MzA2NA.GyVast.5hDmaZ-44lrGW3Xxw3yERnvB9LXHBJ6T7p42ec",
          "MTExNjA0MTA0ODMzOTI3MTc5MQ.GAVK5L.SensjZL0qY4ifycY3mpNKe5JeVIBt5o3QSj60c",
          "MTExNjA1MjA1MDQ4NTE5NDg4Mg.GQFzIi.O4ZEqdM-2Ka0NIKpW09hhWJYF9waNmIwJfpBno"]

selfclient = Client(api_version=10)
selfclient.login(token=tokens)


async def main():

    user: User = selfclient.users[1]

    await user.create_guild_role(
        guild_id=983442350963576863,
        name="tes_role23"
    )


if __name__ == "__main__":
    selfclient.run_async(main())
