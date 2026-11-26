from collections.abc import Iterable
from datetime import datetime
from typing import TypedDict
from urllib import response
from uuid import uuid4

from pydantic import ValidationError

from ..utils.errors import RowTransformError
from .models import NormalizedRow, RawRow, Row, RowCert


class TransformedPayload(TypedDict):
    valid: list[Row]
    invalid: list[RowCert]


def _clean_row(row: RawRow) -> dict[str, str | None]:
    cleaned_row: dict[str, str | None] = {}

    for key, value in row.items():
        if value is None:
            cleaned_row[key] = None
        else:
            stripped_value = value.strip()
            cleaned_row[key] = stripped_value if stripped_value else None

    return cleaned_row


def _normalize_row(row: RawRow) -> NormalizedRow:
    cleaned_row = _clean_row(row)

    normalized_row: NormalizedRow = {}

    normalized_row["id"] = uuid4()

    id_value = cleaned_row.get("id")
    if id_value is not None:
        normalized_row["source_id"] = int(id_value)

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


def _validate_row(row: RawRow) -> Row:
    normalized_row = _normalize_row(row)

    try:
        return Row.model_validate(normalized_row)
    except ValidationError as e:
        raise RowTransformError(str(e)) from e


def transform_rows(rows: Iterable[RawRow]) -> TransformedPayload:
    valid_rows: list[Row] = []
    invalid_rows: list[RowCert] = []

    for id, row in enumerate(rows):
        try:
            result = _validate_row(row)
            valid_rows.append(result)
        except RowTransformError as e:
            invalid_rows.append(
                RowCert.model_construct(
                    row_id=id + 2, row_content=row, error_message=str(e)
                )
            )

    return {"valid": valid_rows, "invalid": invalid_rows}
