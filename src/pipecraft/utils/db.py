import sqlite3
from collections.abc import Sequence
from pathlib import Path
from types import TracebackType
from typing import Any

from ..settings.path import get_path
from .decorators import retry
from .errors import DbError

paths = get_path()
db_path = paths.data_dir / "pipecraft.db"
listing_sql_path = paths.data_dir / "listing.sql"
run_sql_path = paths.data_dir / "run.sql"


class Db:
    def __init__(self, database_path: Path | None = None) -> None:
        self.database_path = database_path or db_path
        self.conn = self.init_connection()
        self.cursor = self.conn.cursor()

    def init_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.database_path)
        return conn

    @retry
    def execute(
        self, query: str, params: str | tuple[object, ...] = ()
    ) -> sqlite3.Cursor:
        try:
            return self.cursor.execute(query, params)
        except sqlite3.Error as e:
            raise DbError(str(e)) from e

    def query_one(self, query: str, params: str | tuple[object, ...] = ()) -> Any:
        result = self.execute(query, params)
        return result.fetchone()

    def query_many(self, query: str, params: str | tuple[object, ...] = ()) -> Any:
        result = self.execute(query, params)
        return result.fetchall()

    def insert_one(self, query: str, payload: tuple[object, ...]) -> int:
        result = self.execute(query, payload)
        self.conn.commit()
        return result.rowcount

    @retry
    def insert_many(self, query: str, payload: Sequence[tuple[object, ...]]) -> int:
        try:
            self.cursor.executemany(query, payload)
            self.conn.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            raise DbError(str(e)) from e

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.conn.close()


def create_table(db: Db, path: Path) -> None:
    with open(path) as dump:
        payload = dump.read()

    try:
        db.cursor.executescript(payload)
        db.conn.commit()
        print("Sql script executed successfully")
    except sqlite3.Error as e:
        print("Failed to create table: ", str(e))
        raise DbError(str(e)) from e


def ensure_table_exists(db: Db) -> None:
    list_exists = db.query_one(
        "SELECT name FROM sqlite_master WHERE name=?", ("listing",)
    )
    run_exists = db.query_one("SELECT name FROM sqlite_master WHERE name=?", ("run",))

    if not list_exists:
        create_table(db, listing_sql_path)
    if not run_exists:
        create_table(db, run_sql_path)


db = Db()


def load_db(d_b: Db | None = None) -> None:
    if d_b is None:
        ensure_table_exists(db)
        return
    ensure_table_exists(d_b)


def get_db(database_path: Path | None = None) -> Db:
    if database_path is None:
        return db
    return Db(database_path)
