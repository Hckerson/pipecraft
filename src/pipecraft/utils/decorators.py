"""Decorators shared across pipecraft modules."""

import functools
import time
from collections.abc import Callable

from pipecraft.settings.config import (
    ERR_INITIAL_DELAY,
    ERR_MAX_ATTEMPT,
)
from pipecraft.utils.errors import process_error


def retry[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        for attempt in range(ERR_MAX_ATTEMPT):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                if not process_error(error) or attempt == ERR_MAX_ATTEMPT - 1:
                    raise
                time.sleep((attempt + 1) * ERR_INITIAL_DELAY)
        raise RuntimeError("retry loop ended unexpectedly")

    return wrapper
