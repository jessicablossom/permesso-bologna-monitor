from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class QuesturaStatus(str, Enum):
    READY = "ready"
    NOT_READY = "not_ready"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BirthDateParts:
    day: str
    month: str
    year: str


@dataclass(frozen=True)
class QuesturaForm:
    action_url: str
    fields: dict[str, str]


@dataclass(frozen=True)
class CheckResult:
    status: QuesturaStatus
    detail: str
    checked_url: str
    response_text: str

    @property
    def is_ready(self) -> bool:
        return self.status is QuesturaStatus.READY


class EmailSettings(Protocol):
    notify_email: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str


@dataclass(frozen=True)
class Settings:
    questura_url: str
    practice_code: str
    birth_date: str
    timezone: str
    notify_email: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
