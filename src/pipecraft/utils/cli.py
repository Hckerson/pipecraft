import argparse

from pipecraft.etl.models import Args

parser = argparse.ArgumentParser(
    prog="Pipecraft", description="Fetches job listing and runs them in a pipeline"
)

parser.add_argument("--db")
parser.add_argument("file")
parser.add_argument("-t", "--test", action="store_true")
parser.add_argument("-p", "--parse", action="store_true")


def get_args() -> Args:
    result = parser.parse_args()
    return Args(
        db=result.db,
        file=result.file,
        test=result.test,
        parse=result.parse,
    )
