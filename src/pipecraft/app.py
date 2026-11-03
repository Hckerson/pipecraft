from pipecraft.etl.pipeline import parse_result, run_pipeline
from pipecraft.settings.path import load_path
from pipecraft.utils.db import load_db


def main() -> None:
    load_path()
    load_db()


if __name__ == "__main__":
    main()
