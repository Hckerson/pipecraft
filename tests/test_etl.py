from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from uuid import UUID

import pytest

from pipecraft.etl import (
    RowTransformError,
    clean_row,
    normalize_row,
    run_pipeline,
    transform_rows,
    validate_row,
)
from pipecraft.etl import pipeline as pipeline_module
from pipecraft.etl.models import Args, Row
from pipecraft.etl.sink import Sink
from pipecraft.utils.db import Db, ensure_table_exists


@pytest.fixture
def isolated_pipeline_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[Db]:
    database = Db(tmp_path / "pipecraft.db")
    ensure_table_exists(database)
    monkeypatch.setattr(
        pipeline_module,
        "get_sink",
        lambda: Sink(database),
    )
    try:
        yield database
    finally:
        database.conn.close()


def test_clean_normalize_and_validate_rows() -> None:
    raw_row = {
        "id": " 7 ",
        "name": " Ada Lovelace ",
        "email": " ada@example.com ",
        "amount": " 42 ",
        "created_at": "2026-10-23T12:30:00",
        "note": "   ",
        "optional": None,
    }

    assert clean_row(raw_row) == {
        "id": "7",
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "amount": "42",
        "created_at": "2026-10-23T12:30:00",
        "note": None,
        "optional": None,
    }

    normalized = normalize_row(raw_row)
    assert isinstance(normalized["id"], UUID)
    assert normalized["source_id"] == 7
    assert normalized["name"] == "Ada Lovelace"
    assert normalized["email"] == "ada@example.com"
    assert normalized["amount"] == 42
    assert normalized["created_at"] == datetime(2026, 10, 23, 12, 30)
    assert normalized["note"] is None
    assert normalized["optional"] is None

    row = validate_row(raw_row)
    assert isinstance(row.id, UUID)
    assert row.source_id == 7
    assert row.amount == 42
    assert row.email == "ada@example.com"


def test_normalize_uses_current_time_when_created_at_is_missing():
    normalized = normalize_row(
        {
            "id": "1",
            "name": "Grace Hopper",
            "email": "grace@example.com",
            "amount": "10",
        }
    )

    assert isinstance(normalized["created_at"], datetime)


def test_validate_row_wraps_pydantic_validation_errors() -> None:
    with pytest.raises(RowTransformError, match="validation error"):
        validate_row(
            {
                "id": "0",
                "name": "",
                "email": "not-an-email",
                "amount": "0",
            }
        )


def test_run_pipeline_and_summarize_csv(
    tmp_path: Path, isolated_pipeline_database: Db
) -> None:
    csv_path = tmp_path / "rows.csv"
    csv_path.write_text(
        "id,name,email,amount,created_at\n"
        "1,Ada,ada@example.com,5,2026-10-23T09:00:00\n"
        "2,Grace,grace@example.com,8,2026-10-23T10:00:00\n",
        encoding="utf-8",
    )

    rows = run_pipeline(str(csv_path), Args(file=str(csv_path)))

    typed_rows = [row for row in rows if isinstance(row, Row)]
    assert len(typed_rows) == 2
    assert all(isinstance(row.id, UUID) for row in typed_rows)
    assert [(row.source_id, row.name, row.amount) for row in typed_rows] == [
        (1, "Ada", 5),
        (2, "Grace", 8),
    ]
    assert [row.created_at for row in typed_rows] == [
        datetime(2026, 10, 23, 9),
        datetime(2026, 10, 23, 10),
    ]
    assert isolated_pipeline_database.query_one(
        "SELECT status, rows_in, rows_out FROM run"
    ) == ("succeeded", 2, 2)


def test_transform_rows_validates_every_row():
    rows = transform_rows(
        [
            {
                "id": "3",
                "name": "Katherine Johnson",
                "email": "katherine@example.com",
                "amount": "12",
            }
        ]
    )

    assert [row.source_id for row in rows] == [3]
