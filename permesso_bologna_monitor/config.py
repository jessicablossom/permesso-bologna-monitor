from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from permesso_bologna_monitor.constants import (
    DEFAULT_QUESTURA_URL,
    DEFAULT_TIMEZONE,
)
from permesso_bologna_monitor.env_utils import env_or_default, required_env
from permesso_bologna_monitor.types import Settings


@dataclass(frozen=True)
class SmtpSettings:
    notify_email: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str


def _smtp_missing_message(smtp_user: str, smtp_password: str) -> str:
    missing: list[str] = []
    if not smtp_user:
        missing.append("SMTP_USER")
    if not smtp_password:
        missing.append("SMTP_PASSWORD")

    if os.environ.get("GITHUB_ACTIONS") == "true":
        return (
            f"Missing GitHub Actions secrets: {', '.join(missing)}. "
            "Configure them in Settings -> Secrets and variables -> Actions."
        )

    return f"Missing {', '.join(missing)} in .env"


def load_smtp_settings() -> SmtpSettings:
    smtp_user = env_or_default("SMTP_USER", "")
    smtp_password = env_or_default("SMTP_PASSWORD", "").replace(" ", "")
    if not smtp_user or not smtp_password:
        raise ValueError(_smtp_missing_message(smtp_user, smtp_password))

    notify_email = env_or_default("NOTIFY_EMAIL", smtp_user)
    if "@" not in notify_email:
        raise ValueError("Invalid NOTIFY_EMAIL; configure a valid email address")

    return SmtpSettings(
        notify_email=notify_email,
        smtp_host=env_or_default("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(env_or_default("SMTP_PORT", "587")),
        smtp_user=smtp_user,
        smtp_password=smtp_password,
    )


def load_settings(env_path: str | None = None) -> Settings:
    load_dotenv(env_path)
    smtp = load_smtp_settings()

    return Settings(
        questura_url=env_or_default("QUESTURA_URL", DEFAULT_QUESTURA_URL),
        practice_code=required_env("QUESTURA_PRACTICE_CODE"),
        birth_date=required_env("QUESTURA_BIRTH_DATE"),
        timezone=env_or_default("TIMEZONE", DEFAULT_TIMEZONE),
        notify_email=smtp.notify_email,
        smtp_host=smtp.smtp_host,
        smtp_port=smtp.smtp_port,
        smtp_user=smtp.smtp_user,
        smtp_password=smtp.smtp_password,
    )
