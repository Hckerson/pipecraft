from sqlite3 import Error as SqliteError

from pipecraft.etl.models import Row, Run
from pipecraft.utils.db import get_db


class Sink:
    def __init__(self) -> None:
        self.db = get_db()

    def insert_listing(self, rows: list[Row]) -> int:
        body = [
            (row.id, row.name, row.email, row.amount, str(row.created_at.isoformat()))
            for row in rows
        ]

        try:
            row_count = self.db.insert_many(
                "INSERT INTO listing VALUES(?, ?, ?, ?, ?)", body
            )
        except:
            raise SqliteError

        return row_count

    def insert_run(self, run: Run) -> int:
        payload = (
            str(run.id),
            run.started_at.isoformat(),
            run.finished_at and run.finished_at.isoformat(),
            str(run.status),
            run.rows_in,
            run.rows_out,
            run.error_message,
        )

        try:
            row_count = self.db.insert_one(
                "INSERT INTO run VALUES(?, ?, ?, ?, ?, ?, ?)", payload
            )
        except:
            raise SqliteError

        return row_count


sink = Sink()


def get_sink() -> Sink:
    return sink
