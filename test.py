from datetime import datetime
from pathlib import Path

import pytest

from pipecraft.etl.models import Row
from pipecraft.etl.pipeline import parse_result, run_pipeline
from pipecraft.etl.transforms import (
    RowTransformError,
    clean_row,
    normalize_row,
    transform_rows,
    validate_row,
)


def test_clean_normalize_and_validate_row() -> None:
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

    assert normalized["id"] == 7
    assert normalized["amount"] == 42
    assert normalized["created_at"] == datetime(2026, 10, 23, 12, 30)
    assert normalized["name"] == "Ada Lovelace"
    assert normalized["note"] is None

    row = validate_row(raw_row)

    assert row.id == 7
    assert row.amount == 42
    assert row.email == "ada@example.com"


def test_normalize_uses_current_time_when_created_at_is_missing() -> None:
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


def test_run_pipeline_and_summarize_csv(tmp_path: Path) -> None:
    csv_path = tmp_path / "rows.csv"
    csv_path.write_text(
        "id,name,email,amount,created_at\n"
        "1,Ada,ada@example.com,5,2026-10-23T09:00:00\n"
        "2,Grace,grace@example.com,8,2026-10-23T10:00:00\n",
        encoding="utf-8",
    )

    rows = run_pipeline(str(csv_path))

    assert rows == [
        Row(
            id=1,
            name="Ada",
            email="ada@example.com",
            amount=5,
            created_at=datetime(2026, 10, 23, 9),
        ),
        Row(
            id=2,
            name="Grace",
            email="grace@example.com",
            amount=8,
            created_at=datetime(2026, 10, 23, 10),
        ),
    ]
    assert parse_result(rows) == {"data": rows, "count": 2}


def test_transform_rows_validates_every_item() -> None:
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

    assert [row.id for row in rows] == [3]
