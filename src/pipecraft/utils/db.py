import sqlite3

from src.pipecraft.settings.path import get_path
from src.pipecraft.settings.config import get_config

paths = get_path()
configs = get_config()
db_path = paths.data_dir / "listing.db"
TABLE_NAME = configs.TABLE_NAME


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

    def insert_row(self, query: str, content: tuple | list[tuple]):
        self.execute(query)
        self.conn.commit()


def ensure_table_exists(db: Db) -> None:
    res = db.execute("SELECT name FROM sqlite_master WHERE name=?", "listing")

    if not res.fetchone():
        with open(db_path, "r") as dump:
            content = dump.read()

        try:
            db.cursor.executescript(content)
            db.conn.commit()
            print("Sql script executed successfully")
        except sqlite3.Error as e:
            print("Failed to create table: ", str(e))


db = Db()


def load_db() -> None:
    ensure_table_exists(db)


def get_db() -> Db:
    return db
