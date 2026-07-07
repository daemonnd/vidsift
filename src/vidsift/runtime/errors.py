class LockingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class LockWritingError(LockingError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# errors for basic init
class BasicInitError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
