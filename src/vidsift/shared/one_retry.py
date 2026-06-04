"""
    File for a one retry decorator for the AI usage manager.
"""

from vidsift.shared.errorprotocol import logger

log: logger = logger()

def retry_once(func):
    """
    Decorator to retry a function once if it raises an exception.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.log_warning(f"Error occurred: {e}. Retrying once...")
            return func(*args, **kwargs)
    return wrapper
