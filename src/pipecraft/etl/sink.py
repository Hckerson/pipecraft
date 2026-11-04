from pipecraft.etl.models import Row
from pipecraft.utils.db import get_db


class Sink:
    def __init__(self) -> None:
        self.sink = get_db()

    def insert_rows(self, rows: list[Row]) -> int:
        body = [
            (row.id, row.name, row.email, row.amount, str(row.created_at.isoformat())) for row in rows
        ]
        row_count = self.sink.insert_rows("INSERT INTO listing VALUES(?, ?, ?, ?, ?)", body)
        return row_count

sink = Sink()

def get_sink()-> Sink:
    return sink