import logging
from logging import FileHandler
from pathlib import Path

from platformdirs import user_log_dir
from rich.console import Console


def get_style(levelname: str) -> str:
    level_styles: dict = {
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold red"
            }
    return level_styles.get(levelname, "white")


class RichConsoleHandler(logging.Handler):
    """
    Class for logging colorful in the console
    """
    def __init__(self):
        super().__init__()
        self.console = Console()
    def emit(self, record):
        message = self.format(record)
        style: str = get_style(message=message, levelname=record.levelname)
        self.console.print(message, style=style)


def configure_logging():
    # get root logger
    logger = logging.getLogger()

    # remove existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.propagate = False
        
    # define the logger, once with a console handler and once with a file handler
    console_handler = RichConsoleHandler()
    #Path(user_log_path(appname="vidsift")).parent.mkdir(parents=True, exist_ok=True)
    #Path(user_log_path(appname="vidsift")).touch(exist_ok=True)
    #file_handler = FileHandler(str(Path(user_log_path(appname="vidsift"))))
        
    # def formatter for file logging handler
    formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
    ) 
    # def formatter for console logging handler
    consoleformatter = logging.Formatter(
        "{levelname}: {message}",
        style="{"
    )

    # set formatters on handlers
    #file_handler.setFormatter(formatter)
    console_handler.setFormatter(consoleformatter)

    # add handler and level to root logger
    logger.addHandler(console_handler)
    #logger.addHandler(file_handler)

    logger.setLevel(logging.DEBUG)


if __name__ == "__main__":
    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("this is an info")
    logger.warning("this is a regular warning")
    logger.error("oh no, this failed :(")
