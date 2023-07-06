from .enums import Permissions


class PermissionBuilder:
    """
    PermissionBuilder takes a Permissions type and then adds them all to a value.
    Methods using PermissionBuilder acquire this value.

    :param args: PermissionType values
    """

    __slots__ = ("value",)

    def __init__(self, *args: Permissions) -> None:

        self.value: int = 0

        for permission in args:
            if isinstance(permission, Permissions):
                self.value += permission.value

    def __repr__(self):
        return f"<PermissionBuilder={self.value}>"
