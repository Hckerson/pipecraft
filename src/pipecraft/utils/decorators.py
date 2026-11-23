"""Decorators shared across pipecraft modules."""








from pipecraft.etl.errors import process_error
from pipecraft.settings.config import ERR_MAX_ATTEMPT




import functools

def retry(func):
    functools.wraps(func)
    def wrapper(*args, **kwargs):
        count = ERR_MAX_ATTEMPT
        try:
            x = func(*args, **kwargs)
            return x
        except Exception as e:
            should_retry = process_error(e)
            if should_retry and count > 0:
                count -= 1
                x = func(*args, **kwargs)
                return x
    return wrapper