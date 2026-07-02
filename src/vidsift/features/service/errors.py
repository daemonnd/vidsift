class ServiceError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class OSNotSupportedError(ServiceError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ServiceExecutionError(ServiceError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
