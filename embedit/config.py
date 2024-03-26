from __future__ import annotations

import tomllib
from typing import TypedDict


class SqliteConfig(TypedDict):
    file: str


class Config(TypedDict):
    url: str
    repo: str
    color: str
    sqlite: SqliteConfig


def _load_config() -> Config:
    with open("config.toml") as fp:
        text = fp.read()
    return tomllib.loads(text)  # type: ignore - it's loading the config.


CONFIG = _load_config()
