import sqlite3
from pathlib import Path

from pipecraft.settings.path import get_path

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

    def execute(self, query: str, params: str | tuple = ()):
        return self.cursor.execute(query, params)

    def query_one(self, query: str, params: str | tuple = ()):
        result = self.execute(query, params)
        return result.fetchone()

    def query_many(self, query: str, params: str | tuple = ()):
        result = self.execute(query, params)
        return result.fetchall()

    def insert_one(self, query: str, payload: tuple) -> int:
        self.cursor.execute(query, payload)
        self.conn.commit()
        return self.cursor.rowcount

    def insert_many(self, query: str, payload: list[tuple]) -> int:
        self.cursor.executemany(query, payload)
        self.conn.commit()
        return self.cursor.rowcount

    def __exit__(self, exc_type, exc, tb):
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


def load_db() -> None:
    ensure_table_exists(db)


def get_db(database_path: Path | None = None) -> Db:
    if database_path is None:
        return db
    return Db(database_path)
