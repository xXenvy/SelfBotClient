from enum import Enum
from .enums import Permissions


class PermissionBuilder:
    __slots__ = ("value",)

    def __init__(self, *args: Permissions):
        """
        The __init__ function is the constructor for a class. It's called when you create an instance of the class,
        and it allows you to set up all attributes and other things that your object will need.


        :param self: Refer to the instance of the class
        :param *args: tuple[Permissions]: Accept a variable number of arguments
        :return: Nothing
        """

        self.value: int = 0

        for permission in args:
            if isinstance(permission, Enum):
                self.value += permission.value

    def __repr__(self):
        return f"<PermissionBuilder={self.value}>"
