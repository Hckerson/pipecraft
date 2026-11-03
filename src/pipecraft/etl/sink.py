from pathlib import Path
from src.pipecraft.utils.db import get_db


def db_sink(path: Path) -> None:
    sq_lite = get_db()

    pass
