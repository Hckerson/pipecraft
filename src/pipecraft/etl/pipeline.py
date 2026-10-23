from typing import TypedDict

from .models import Row
from .source import parse_csv
from .transforms import transform_rows


class PipelineResult(TypedDict):
    data: list[Row]
    count: int


def run_pipeline(path: str) -> list[Row]:
    rows = parse_csv(path)
    return transform_rows(rows)


def parse_result(rows: list[Row]) -> PipelineResult:
    return {"data": rows, "count": len(rows)}
