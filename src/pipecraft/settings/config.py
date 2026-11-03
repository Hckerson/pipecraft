from dataclasses import dataclass


@dataclass
class AppConfig:
    TABLE_NAME = "listings"


def get_config() -> AppConfig:
    config = AppConfig()
    return config
