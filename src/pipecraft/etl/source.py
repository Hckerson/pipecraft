import csv
from collections.abc import Iterator

from pipecraft.etl.models import RawRow


def parse_csv(path: str) -> list[dict[str, str | None]]:
    with open(path, newline="", encoding="utf-8") as file:
        reader: Iterator[RawRow] = csv.DictReader(file)
        return [row for row in reader]
