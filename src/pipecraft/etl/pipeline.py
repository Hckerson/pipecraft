from csv import Error as CsvError
from datetime import datetime
from sqlite3 import Error as SqliteError
from typing import TypedDict

from .models import Args, Row, Run, RunStatus
from .sink import get_sink
from .source import parse_csv
from .transforms import RowTransformError, transform_rows



def run_pipeline(path: str, args: Args) -> list[Row]:
    run: dict[str, object] = {
        "started_at": datetime.now(),
        "rows_in": 0,
        "rows_out": 0,
        "status": RunStatus.RUNNING,
    }
    sink = get_sink()

    try:
        rows = parse_csv(path)
        run["rows_in"] = len(rows)

        transformed_rows = transform_rows(rows)
        row_count = sink.insert_listing(transformed_rows)
        run["rows_out"] = row_count
        run["status"] = RunStatus.SUCCEEDED

        return transformed_rows

    except (
        CsvError,
        SqliteError,
        RowTransformError,
        FileNotFoundError,
        ValueError,
    ) as err:
        run["rows_out"] = 0
        run["status"] = RunStatus.FAILED
        run["error_message"] = str(err)
        return []

    finally:
        run["finished_at"] = datetime.now()
        sink.insert_run(Run.model_validate(run))



