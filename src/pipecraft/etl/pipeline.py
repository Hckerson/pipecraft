from typing import TypedDict
from datetime import datetime
from csv import Error as CsvError
from sqlite3 import Error as SqliteError

from .models import Row, Run
from .sink import get_sink
from .source import parse_csv
from .transforms import transform_rows


class PipelineResult(TypedDict):
    data: list[Row]
    count: int


def run_pipeline(path: str) :

    run = {}
    sink = get_sink()

    try:
        run["started_at"] = datetime.now()
        rows = parse_csv(path)
        run["rows_in"] = len(rows)
        run["status"] = "running"

        transformed_rows = transform_rows(rows)
        row_count = sink.insert_listing(transformed_rows)
        run["finished_at"] = datetime.now()
        run["rows_out"] = row_count

        if not row_count:
            run["status"] = "failed"
        else:
            run["status"] = "succeeded"

        return transformed_rows
        run_dump = Run.model_validate(run)
    except (CsvError, SqliteError) as err :
        run["error_message"] = str(err)


        return []


def parse_result(rows: list[Row]) -> PipelineResult:
    return {"data": rows, "count": len(rows)}
