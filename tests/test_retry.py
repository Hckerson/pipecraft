import pytest

from pipecraft.settings.config import ERR_MAX_ATTEMPT
from pipecraft.utils.decorators import retry
from pipecraft.utils.errors import DbError


def test_retry_returns_result_after_temporary_failures() -> None:
    attempts = [0]

    @retry
    def operation() -> str:
        attempts[0] += 1
        if attempts[0] < 3:
            raise DbError("temporary failure")
        return "success"

    assert operation() == "success"
    assert attempts[0] == 3


def test_retry_raises_after_maximum_attempts() -> None:
    attempts = [0]

    @retry
    def operation() -> str:
        attempts[0] += 1
        raise DbError("persistent failure")

    with pytest.raises(DbError, match="persistent failure"):
        operation()

    assert attempts[0] == ERR_MAX_ATTEMPT


def test_retry_does_not_retry_non_retryable_errors() -> None:
    attempts = [0]

    @retry
    def operation() -> str:
        attempts[0] += 1
        raise ValueError("invalid input")

    with pytest.raises(ValueError, match="invalid input"):
        operation()

    assert attempts[0] == 1
