from __future__ import annotations

import os


def env_or_default(key: str, default: str) -> str:
    value = os.environ.get(key, "").strip()
    return value if value else default


def required_env(key: str) -> str:
    value = env_or_default(key, "")
    if value:
        return value
    raise ValueError(f"Missing {key} in .env or GitHub Actions secrets")
