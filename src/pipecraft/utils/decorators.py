"""Decorators shared across pipecraft modules."""

import functools
from collections.abc import Callable

from pipecraft.settings.config import ERR_MAX_ATTEMPT
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
        raise RuntimeError("retry loop ended unexpectedly")

    return wrapper
