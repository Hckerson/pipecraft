from pathlib import Path

import pytest

from pipecraft import app
from pipecraft.etl.models import Row
from pipecraft.etl.pipeline import PipelineResult
from pipecraft.settings.path import AppConfig


def test_main_runs_pipeline_and_prints_summary(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    row = Row(id=1, name="Ada", email="ada@example.com", amount=5)
    summary: PipelineResult = {"data": [row], "count": 1}

    def fake_load_config() -> None:
        return None

    def fake_get_config() -> AppConfig:
        return AppConfig(root=tmp_path)

    def fake_run_pipeline(path: str) -> list[Row]:
        assert path == str(tmp_path / "data" / "sample.csv")
        return [row]

    def fake_parse_result(rows: list[Row]) -> PipelineResult:
        assert rows == [row]
        return summary

    monkeypatch.setattr(app, "load_config", fake_load_config)
    monkeypatch.setattr(app, "get_config", fake_get_config)
    monkeypatch.setattr(app, "run_pipeline", fake_run_pipeline)
    monkeypatch.setattr(app, "parse_result", fake_parse_result)

    app.main()

    assert capsys.readouterr().out == f"{summary}\n"
