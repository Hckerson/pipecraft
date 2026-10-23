from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class AppConfig:
    root: Path = PROJECT_ROOT

    @property
    def data_dir(self) -> Path:
        return self.root / "data"

    @property
    def docs_dir(self) -> Path:
        return self.root / "docs"

    @property
    def config_dir(self) -> Path:
        return self.root / "config"


def ensure_dirs(config: AppConfig) -> None:
    for directory in (config.data_dir, config.docs_dir, config.config_dir):
        directory.mkdir(parents=True, exist_ok=True)


config = AppConfig()


def load_config() -> None:
    ensure_dirs(config)


def get_config() -> AppConfig:
    return config
