import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from platformdirs import user_log_dir

from vidsift.config.models import AppConfig
from vidsift.shared.logging.filters import ConsoleDependencyFilter, FileDependencyFilter
from vidsift.shared.logging.formatters import JSONFormatter, ConsoleFormatter
from vidsift.shared.logging.handlers import RichConsoleHandler


def get_log_file_path() -> Path:
    Path(user_log_dir(appname="vidsift")).mkdir(parents=True, exist_ok=True)
    user_log_file: Path = Path(f"{user_log_dir(appname='vidsift')}/vidsift.jsonl")
    return user_log_file


def configure_logging(config: AppConfig):
    file_config = config.logging.file
    console_config = config.logging.console

    # get root logger
    logger = logging.getLogger()

    # remove existing handlers
    # if logger.hasHandlers():
    #    logger.handlers.clear()
    for hander in logger.handlers[:]:
        hander.close()
        logger.removeHandler(hander)
    # logger.propagate = False

    # define the logger, once with a console handler and once with a file handler
    console_handler = RichConsoleHandler()

    file_handler = TimedRotatingFileHandler(
        filename=str(get_log_file_path()),
        when=file_config.rotation,
        interval=1,
        backupCount=file_config.retain_days,
        utc=file_config.utc_time,
    )

    # get filter instances
    console_dependeny_filter: ConsoleDependencyFilter = ConsoleDependencyFilter(
        console_config=console_config
    )
    file_dependency_filter: FileDependencyFilter = FileDependencyFilter(
        file_config=file_config
    )

    # console handler config
    console_handler.setFormatter(ConsoleFormatter())
    console_handler.addFilter(console_dependeny_filter)
    console_handler.setLevel(logging.DEBUG)

    # file handler config
    file_handler.setFormatter(JSONFormatter())
    file_handler.addFilter(file_dependency_filter)
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
    logger = logging.getLogger("dependency")
    print("SWICHTED LOGGER")
    logger.debug("this should not be printed")
    logger.info("this nether")
    logger.warning("this should be printed")
    logger.error("this is an error")
    logger.critical("oh, no! this error is so bad!")
