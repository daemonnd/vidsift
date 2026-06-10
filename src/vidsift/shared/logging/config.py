import logging
from logging import FileHandler
from pathlib import Path

from platformdirs import user_log_dir

from vidsift.shared.logging.filters import DependencyFilter
from vidsift.shared.logging.formatters import JSONFormatter, consoleformatter
from vidsift.shared.logging.handlers import RichConsoleHandler


def get_log_file_path() -> Path:
    Path(user_log_dir(appname="vidsift")).mkdir(parents=True, exist_ok=True)
    user_log_file: Path = Path(f"{user_log_dir(appname="vidsift")}/vidsift.jsonl")
    Path(user_log_file).touch(exist_ok=True)
    return user_log_file

def configure_logging():
    # get root logger
    logger = logging.getLogger()

    # remove existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    #logger.propagate = False
 
    # define the logger, once with a console handler and once with a file handler
    console_handler = RichConsoleHandler()
    file_handler = FileHandler(str(get_log_file_path()))
 
    # def formatter for file logging handler
    formatter = logging.Formatter(
        "{asctime} - {levelname} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # get filter instance
    depencendy_filter = DependencyFilter(debug_mode=True)

    # console handler config
    console_handler.setFormatter(consoleformatter)
    console_handler.addFilter(depencendy_filter)
    console_handler.setLevel(logging.DEBUG)

    # file handler config
    file_handler.setFormatter(JSONFormatter())
    file_handler.addFilter(depencendy_filter)
    file_handler.setLevel(logging.DEBUG)

    # add handler and level to root logger
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)




if __name__ == "__main__":
    configure_logging()
    logger = logging.getLogger("vidsift")
    logger.debug("this is a debug statement")
    logger.info("this is an info")
    logger.warning("this is a regular warning")
    logger.error("oh no, this failed :(")
    logger.critical("this is a critical error, oh no")
