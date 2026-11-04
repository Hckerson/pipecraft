import sqlite3

from pipecraft.settings.path import get_path

paths = get_path()
db_path = paths.data_dir / "listing.db"
sql_path = paths.data_dir / "listing.sql"


class Db:
    def __init__(self) -> None:
        self.conn = self.init_connection()
        self.cursor = self.conn.cursor()

    def init_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(db_path)
        return conn

    def execute(self, query: str, params: str | tuple = ()):
        return self.cursor.execute(query, params)

    def query_one(self, query: str, params: str | tuple = ()):
        result = self.execute(query, params)
        return result.fetchone()

    def query_many(self, query: str, params: str | tuple = ()):
        result = self.execute(query, params)
        return [row for row in result.fetchmany()]

    def insert_row(self, query: str, payload: tuple) -> int:
        self.cursor.execute(query, payload)
        self.conn.commit()
        return self.cursor.rowcount

    def insert_rows(self, query: str, payload: list[tuple]) -> int:
        self.cursor.executemany(query, payload)
        self.conn.commit()
        return self.cursor.rowcount

    def __exit__(self, exc_type, exc, tb):
        self.conn.close()


def ensure_table_exists(db: Db) -> None:
    res = db.execute("SELECT name FROM sqlite_master WHERE name=?", ("listing",))

    if not res.fetchone():
        with open(sql_path, "r") as dump:
            payload = dump.read()

        try:
            db.cursor.executescript(payload)
            db.conn.commit()
            print("Sql script executed successfully")
        except sqlite3.Error as e:
            print("Failed to create table: ", str(e))


db = Db()


def load_db() -> None:
    ensure_table_exists(db)


def get_db() -> Db:
    return db
