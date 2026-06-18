from __future__ import annotations

import os

from permesso_bologna_monitor.types import Settings


def make_settings(**overrides: object) -> Settings:
    defaults = {
        "questura_url": "https://www.questura.bologna.it/node/2",
        "practice_code": "08BO012345",
        "birth_date": "01/02/1980",
        "timezone": "Europe/Rome",
        "notify_email": "dest@test.com",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "sender@test.com",
        "smtp_password": "secret",
    }
    defaults.update(overrides)
    return Settings(**defaults)


def patch_env(**values: str) -> dict[str, str | None]:
    previous: dict[str, str | None] = {}
    for key, value in values.items():
        previous[key] = os.environ.get(key)
        os.environ[key] = value
    return previous


def restore_env(previous: dict[str, str | None]) -> None:
    for key, value in previous.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
