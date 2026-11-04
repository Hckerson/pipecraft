from typing import TypedDict

from .models import Row
from .sink import get_sink
from .source import parse_csv
from .transforms import transform_rows


class PipelineResult(TypedDict):
    data: list[Row]
    count: int



def run_pipeline(path: str) -> list[Row]:
    sink = get_sink()
    rows = parse_csv(path)
    transformed_rows = transform_rows(rows)
    row_count = sink.insert_rows(transformed_rows)

    if row_count == len(transformed_rows):
        return transformed_rows
    return []


def parse_result(rows: list[Row]) -> PipelineResult:
    return {"data": rows, "count": len(rows)}
