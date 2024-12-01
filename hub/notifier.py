

from functools import wraps
import logging
import subprocess
from typing import Callable


def send_notification(title, message):
    # Construct the AppleScript command
    script = f'display notification "{message}" with title "{title}"'
    # Use subprocess to call osascript
    subprocess.run(["osascript", "-e", script])


def notify(title: str, message: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            send_notification(title, message)
            result = func(*args, **kwargs)
            logging.info(result)
            send_notification(title, result)
            return result

        return wrapper

    return decorator
