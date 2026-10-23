from collections.abc import Iterable, Mapping
from datetime import datetime

from pydantic import ValidationError

from .models import Row

RawRow = Mapping[str, str | None]
NormalizedRow = dict[str, str | int | datetime | None]


class RowTransformError(ValueError):
    pass


def clean_row(row: RawRow) -> dict[str, str | None]:
    cleaned_row: dict[str, str | None] = {}

    for key, value in row.items():
        if value is None:
            cleaned_row[key] = None
        else:
            stripped_value = value.strip()
            cleaned_row[key] = stripped_value if stripped_value else None

    return cleaned_row


def normalize_row(row: RawRow) -> NormalizedRow:
    cleaned_row = clean_row(row)

    normalized_row: NormalizedRow = {}

    id_value = cleaned_row.get("id")
    if id_value is not None:
        normalized_row["id"] = int(id_value)

    amount_value = cleaned_row.get("amount")
    if amount_value is not None:
        normalized_row["amount"] = int(amount_value)

    created_at = cleaned_row.get("created_at")
    if created_at is None:
        normalized_row["created_at"] = datetime.now()
    else:
        normalized_row["created_at"] = datetime.fromisoformat(created_at)

    for key, value in cleaned_row.items():
        if key not in normalized_row:
            normalized_row[key] = value

    return normalized_row


def validate_row(row: RawRow) -> Row:
    normalized_row = normalize_row(row)

    try:
        return Row.model_validate(normalized_row)
    except ValidationError as e:
        raise RowTransformError(str(e)) from e


def transform_rows(rows: Iterable[RawRow]) -> list[Row]:
    return [validate_row(row) for row in rows]
