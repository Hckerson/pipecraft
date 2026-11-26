from datetime import datetime
from pathlib import Path

from pipecraft.utils.db import get_db, load_db

from ..utils.errors import DbError, ParseError, PipelineError, RowTransformError
from .models import Args, RowCert, Run, RunStatus
from .sink import get_sink
from .source import parse_csv
from .transforms import TransformedPayload, transform_rows


def run_pipeline(path: str, args: Args) -> TransformedPayload:

    if not args.file:
        raise PipelineError("Missing file argument")

    run: dict[str, object] = {
        "started_at": datetime.now(),
        "rows_in": 0,
        "rows_out": 0,
        "status": RunStatus.RUNNING,
    }

    if args.db:
        db = get_db(Path(args.db))
        load_db(db)
        sink = get_sink(db)
    else:
        load_db()
        sink = get_sink()

    try:
        rows = parse_csv(path)

        run["rows_in"] = len(rows)
        transformed_rows = transform_rows(rows)

        if args.test:
            return transformed_rows

        valid_rows = transformed_rows.get("valid") or []
        row_count = sink.insert_listing(valid_rows)
        run["rows_out"] = row_count
        run["status"] = RunStatus.SUCCEEDED

        return transformed_rows

    except (
        ParseError,
        DbError,
        RowTransformError,
    ) as err:
        run["rows_out"] = 0
        run["status"] = RunStatus.FAILED
        run["error_message"] = str(err)
        return {"valid": [], "invalid": []}

    finally:
        run["finished_at"] = datetime.now()
        if not args.test:
            sink.insert_run(Run.model_validate(run))
