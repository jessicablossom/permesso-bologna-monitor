from __future__ import annotations

import logging
import re
import unicodedata
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin

import requests

from permesso_bologna_monitor.constants import (
    FIELD_BIRTH_DAY,
    FIELD_BIRTH_MONTH,
    FIELD_BIRTH_YEAR,
    FIELD_PRACTICE_CODE,
    FIELD_REGISTERED_MAIL,
    FIELD_SUBMIT,
    QUESTURA_FORM_ID,
    QUESTURA_NOT_READY_MESSAGE,
    QUESTURA_READY_MESSAGES,
    QUESTURA_SUBMIT_VALUE,
    REQUEST_TIMEOUT_SECONDS,
    USER_AGENT,
)
from permesso_bologna_monitor.types import (
    BirthDateParts,
    CheckResult,
    QuesturaForm,
    QuesturaStatus,
    Settings,
)

logger = logging.getLogger(__name__)


class QuesturaFormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.inside_target_form = False
        self.form_found = False
        self.action_url = ""
        self.fields: dict[str, str] = {}

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)
        if tag == "form":
            self.inside_target_form = attributes.get("id") == QUESTURA_FORM_ID
            if self.inside_target_form:
                self.form_found = True
                self.action_url = attributes.get("action") or ""
            return

        if tag != "input" or not self.inside_target_form:
            return

        name = attributes.get("name")
        if name:
            self.fields[name] = attributes.get("value") or ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "form" and self.inside_target_form:
            self.inside_target_form = False


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip_depth = 0
        self.chunks: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag in {"script", "style"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.chunks.append(data)

    @property
    def text(self) -> str:
        return normalize_whitespace(" ".join(self.chunks))


def create_http_session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    return session


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


def normalize_for_match(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", normalize_whitespace(value))
    without_marks = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return without_marks.casefold()


def parse_birth_date(value: str) -> BirthDateParts:
    parts = value.strip().replace("/", "-").split("-")
    if len(parts) != 3:
        raise ValueError("QUESTURA_BIRTH_DATE must use dd/mm/yyyy or dd-mm-yyyy format")

    day, month, year = (part.strip() for part in parts)
    if not (day.isdigit() and month.isdigit() and year.isdigit()):
        raise ValueError("QUESTURA_BIRTH_DATE must only contain numbers and separators")
    if len(year) != 4:
        raise ValueError("QUESTURA_BIRTH_DATE year must use four digits")

    return BirthDateParts(day=day.zfill(2), month=month.zfill(2), year=year)


def extract_questura_form(html: str, page_url: str) -> QuesturaForm:
    parser = QuesturaFormParser()
    parser.feed(html)
    if not parser.form_found:
        raise ValueError("Questura form was not found")

    return QuesturaForm(
        action_url=urljoin(page_url, parser.action_url or page_url),
        fields=dict(parser.fields),
    )


def build_payload(
    form: QuesturaForm,
    practice_code: str,
    birth_date: str,
) -> dict[str, str]:
    date_parts = parse_birth_date(birth_date)
    payload = dict(form.fields)
    payload[FIELD_REGISTERED_MAIL] = ""
    payload[FIELD_PRACTICE_CODE] = practice_code.strip()
    payload[FIELD_BIRTH_DAY] = date_parts.day
    payload[FIELD_BIRTH_MONTH] = date_parts.month
    payload[FIELD_BIRTH_YEAR] = date_parts.year
    payload.setdefault(FIELD_SUBMIT, QUESTURA_SUBMIT_VALUE)
    return payload


def extract_visible_text(html: str) -> str:
    parser = VisibleTextParser()
    parser.feed(html)
    return parser.text


def classify_response(response_text: str) -> tuple[QuesturaStatus, str]:
    normalized = normalize_for_match(response_text)
    if normalize_for_match(QUESTURA_NOT_READY_MESSAGE) in normalized:
        return QuesturaStatus.NOT_READY, "The permit does not appear ready yet."

    for message in QUESTURA_READY_MESSAGES:
        if normalize_for_match(message) in normalized:
            return QuesturaStatus.READY, "The permit appears ready for pickup."

    return QuesturaStatus.UNKNOWN, "Unrecognized response; check manually."


def check_permesso(
    settings: Settings,
    session: requests.Session | None = None,
) -> CheckResult:
    http = session or create_http_session()
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    logger.info("Fetching Questura form: %s", settings.questura_url)
    form_response = http.get(
        settings.questura_url,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    form_response.raise_for_status()

    form = extract_questura_form(form_response.text, settings.questura_url)
    payload = build_payload(form, settings.practice_code, settings.birth_date)

    logger.info("Submitting permit check to Questura Bologna")
    result_response = http.post(
        form.action_url,
        data=payload,
        headers=headers,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    result_response.raise_for_status()

    response_text = extract_visible_text(result_response.text)
    status, detail = classify_response(response_text)
    return CheckResult(
        status=status,
        detail=detail,
        checked_url=form.action_url,
        response_text=response_text,
    )
