from pathlib import Path

import pytest

from pipecraft import app
from pipecraft.etl.models import Args, Row
from pipecraft.settings.path import AppPath


def test_main_runs_pipeline_and_prints_rows(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    row = Row(name="Ada", email="ada@example.com", amount=5, source_id=1)
    args = Args(file="sample.csv")

    def fake_load_path() -> None:
        return None

    def fake_get_path() -> AppPath:
        return AppPath(root=tmp_path)

    def fake_get_args() -> Args:
        return args

    def fake_run_pipeline(path: str, received_args: Args) -> list[Row]:
        assert path == str(tmp_path / "data" / "sample.csv")
        assert received_args == args
        return [row]

    monkeypatch.setattr(app, "load_path", fake_load_path)
    monkeypatch.setattr(app, "get_path", fake_get_path)
    monkeypatch.setattr(app, "get_args", fake_get_args)
    monkeypatch.setattr(app, "run_pipeline", fake_run_pipeline)

    app.main()

    assert capsys.readouterr().out == f"{[row]}\n"
