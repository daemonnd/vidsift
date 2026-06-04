class ConfigError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ConfigFileNotFoundError(ConfigError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ConfigFilePermissionError(ConfigError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
