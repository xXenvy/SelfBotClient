__all__: tuple[str, ...] = (
    "UnSupportedApiVersion",
    "UnSupportedTokenType",
    "SelfBotClientException",
    "InvalidMethodType"
)


class SelfBotClientException(Exception):
    pass


class UnSupportedApiVersion(SelfBotClientException):

    def __init__(self) -> None:
        super().__init__(
            "Invalid Api Version. Currently supported versions: 10, 9"
        )


class UnSupportedTokenType(SelfBotClientException):

    def __init__(self) -> None:
        super().__init__(
            "Invalid token/s type. Use list[str] or str."
        )


class InvalidMethodType(SelfBotClientException):

    def __init__(self, method: str) -> None:
        super().__init__(
            f"Invalid method {method} type. Available methods: POST, DELETE, GET, PATCH"
        )
