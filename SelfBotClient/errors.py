__all__: tuple[str, ...] = (
    "UnSupportedApiVersion",
    "UnSupportedTokenType",
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


class InvalidStatusType(SelfBotClientException):
    
    def __init__(self, excepted, got):
        super().__init__(f"InvalidStatusType. Expected: {excepted} type got: {got} type.")


class MessagesLimitException(SelfBotClientException):

    def __init__(self, message: str):
        super().__init__(message)