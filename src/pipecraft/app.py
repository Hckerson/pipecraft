from pipecraft.etl.pipeline import parse_result, run_pipeline
from pipecraft.settings.path import load_path, get_path
from pipecraft.utils.db import load_db


def main() -> None:
    load_path()
    load_db()

    path = get_path()
    file_path = path.data_dir / "sample.csv"
    rows = run_pipeline(str(file_path))
    parsed = parse_result(rows)
    print(parsed)


if __name__ == "__main__":
    main()
