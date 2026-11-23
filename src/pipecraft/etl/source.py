import csv
from collections.abc import Iterator

from pipecraft.etl.models import RawRow

class ParseError(Exception):
    pass


def parse_csv(path: str) -> list[RawRow]:
    try:
        with open(path, newline="", encoding="utf-8") as file:
            reader: Iterator[RawRow] = csv.DictReader(file, strict=True)
            return [row for row in reader]
        
    except (csv.Error, FileNotFoundError) as e:
        raise ParseError(str(e)) from e