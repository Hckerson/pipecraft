import sys

import pytest

from pipecraft.utils.cli import get_args


def test_get_args_parses_file_database_and_flags(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pipecraft",
            "sample.csv",
            "--db",
            "custom.db",
            "--parse",
            "--test",
        ],
    )

    args = get_args()

    assert args.file == "sample.csv"
    assert args.db == "custom.db"
    assert args.parse is True
    assert args.test is True
