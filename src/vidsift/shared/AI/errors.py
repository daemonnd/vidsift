
class AIError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InvalidAIResponseFormatError(AIError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class EmptyAIResponseError(AIError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
