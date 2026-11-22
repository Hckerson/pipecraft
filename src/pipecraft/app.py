from pipecraft.etl.pipeline import run_pipeline
from pipecraft.settings.path import get_path, load_path
from pipecraft.utils.db import load_db
from pipecraft.utils.cli import get_args


def main() -> None:
    load_path()
    load_db()

    path = get_path()
    args = get_args()
    file_path = path.data_dir / args.file
    rows = run_pipeline(str(file_path), args)


if __name__ == "__main__":
    main()
