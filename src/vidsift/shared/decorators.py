"""
File for a one retry decorator for the AI usage manager.
"""
import logging

logger = logging.getLogger(__name__)

def retry_once(func):
    """
    Decorator to retry a function once if it raises an exception.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Error occurred: {e}. Retrying once...")
            return func(*args, **kwargs)
        except BaseException:
            raise
    return wrapper
