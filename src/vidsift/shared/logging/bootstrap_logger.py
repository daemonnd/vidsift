import logging


def setup_bootstrap_logging():
    logging.basicConfig()
    logger = logging.getLogger()

    # remove existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
 
    # add handler and level to root logger
    logger.setLevel(logging.INFO)


