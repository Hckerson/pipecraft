from pipecraft.etl.pipeline import run_pipeline
from pipecraft.settings.path import get_path, load_path
from pipecraft.utils import get_args


def main() -> None:
    load_path()

    path = get_path()
    args = get_args()
    file_path = path.data_dir / args.file
    rows = run_pipeline(str(file_path), args)

    print(rows)

if __name__ == "__main__":
    main()
