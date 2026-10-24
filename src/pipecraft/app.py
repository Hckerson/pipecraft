from pipecraft.settings.path import get_config, load_config
from pipecraft.etl.pipeline import parse_result, run_pipeline


def main() -> None:
    load_config()
    configs = get_config()
    sample_path = configs.data_dir / "sample.csv"
    rows = run_pipeline(str(sample_path))
    summary = parse_result(rows)
    print(summary)


if __name__ == "__main__":
    main()
