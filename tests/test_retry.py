import sqlite3
from pathlib import Path

import pytest

from pipecraft.settings.config import ERR_MAX_ATTEMPT
from pipecraft.utils import decorators
from pipecraft.utils.db import Db
from pipecraft.utils.errors import DbError


def test_retry_returns_result_after_temporary_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = [0]
    delays: list[float] = []
    monkeypatch.setattr(decorators.time, "sleep", delays.append)

    @decorators.retry
    def operation() -> str:
        attempts[0] += 1
        if attempts[0] < 3:
            raise DbError("temporary failure", 5)
        return "success"

    assert operation() == "success"
    assert attempts[0] == 3
    assert delays == [1, 2]


def test_retry_raises_after_maximum_attempts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = [0]
    delays: list[float] = []
    monkeypatch.setattr(decorators.time, "sleep", delays.append)

    @decorators.retry
    def operation() -> str:
        attempts[0] += 1
        raise DbError("persistent failure", 5)

    with pytest.raises(DbError, match="persistent failure"):
        operation()

    assert attempts[0] == ERR_MAX_ATTEMPT
    assert delays == [1, 2]


def test_retry_does_not_retry_non_retryable_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = [0]
    delays: list[float] = []
    monkeypatch.setattr(decorators.time, "sleep", delays.append)

    @decorators.retry
    def operation() -> str:
        attempts[0] += 1
        raise DbError("duplicate key", 19)

    with pytest.raises(DbError, match="duplicate key"):
        operation()

    assert attempts[0] == 1
    assert delays == []


def test_database_constraint_error_preserves_code_without_retrying(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    delays: list[float] = []
    monkeypatch.setattr(decorators.time, "sleep", delays.append)
    database = Db(tmp_path / "retry.db")

    try:
        database.execute("CREATE TABLE records (id INTEGER PRIMARY KEY)")
        database.execute("INSERT INTO records (id) VALUES (?)", (1,))

        with pytest.raises(DbError, match="UNIQUE constraint failed") as error:
            database.execute("INSERT INTO records (id) VALUES (?)", (1,))

        assert error.value.sqlite_errorcode == sqlite3.SQLITE_CONSTRAINT_PRIMARYKEY
        assert delays == []
    finally:
        database.conn.close()


def test_database_busy_error_retries_after_lock_is_released(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    database_path = tmp_path / "busy.db"
    database = Db(database_path)
    lock_connection = sqlite3.connect(database_path, timeout=0)
    delays: list[float] = []

    def release_lock(delay: float) -> None:
        delays.append(delay)
        lock_connection.commit()

    try:
        database.execute("CREATE TABLE records (id INTEGER PRIMARY KEY)")
        database.conn.execute("PRAGMA busy_timeout = 0")
        lock_connection.execute("BEGIN EXCLUSIVE")
        monkeypatch.setattr(decorators.time, "sleep", release_lock)

        database.execute("INSERT INTO records (id) VALUES (?)", (1,))
        database.conn.commit()

        assert database.query_one("SELECT id FROM records") == (1,)
        assert delays == [1]
    finally:
        lock_connection.close()
        database.conn.close()
