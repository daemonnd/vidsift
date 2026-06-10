import logging

from rich.console import Console

from vidsift.shared.logging.formatters import get_style


class RichConsoleHandler(logging.Handler):
    """
    Class for logging colorful in the console
    """
    def __init__(self):
        super().__init__()
        self.console = Console()
    def emit(self, record):
        print("type")
        print(type(record.exc_info))
        print("exc_info")
        print(record.exc_info)
        message = self.format(record)
        style: str = get_style(levelname=record.levelname)
        self.console.print(message, style=style)


