from .typings import SESSION


class UserClient:

    def __init__(self, data: dict, session: SESSION):
        self._session: SESSION = session
        self.data: dict = data

        self.token: str = self.data.get("token")
        self.name: str = self.data.get("username")
        self.discriminator: str = f"#{self.data.get('discriminator')}"
        self.id: int = self.data.get("id")

    def __repr__(self):

        return f"<UserClient(name={self.name}, discriminator={self.discriminator}, id={self.id})>"