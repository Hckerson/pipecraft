from pipecraft.etl.models import Row, Run
from pipecraft.utils.db import Db, get_db


class Sink:
    def __init__(self, database: Db | None = None) -> None:
        self.db = database or get_db()

    def insert_listing(self, rows: list[Row]) -> int:
        payload = [
            (row.id, row.name, row.email, row.amount, str(row.created_at.isoformat()))
            for row in rows
        ]

        row_count = self.db.insert_many(
            "INSERT INTO listing (id, name, email, amount, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            payload,
        )
        return row_count

    def insert_run(self, run: Run) -> int:
        payload = (
            str(run.id),
            run.rows_in,
            run.rows_out,
            str(run.status),
            run.error_message,
            run.started_at.isoformat(),
            run.finished_at and run.finished_at.isoformat(),
        )

        row_count = self.db.insert_one(
            "INSERT INTO run "
            "(id, rows_in, rows_out, status, error_message, started_at, finished_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            payload,
        )

        return row_count


sink = Sink()


def get_sink(database: Db | None = None) -> Sink:
    if database is None:
        return sink
    return Sink(database)
