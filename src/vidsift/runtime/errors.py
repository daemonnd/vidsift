class LockingError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class MoreThanOneRowError(LockingError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
