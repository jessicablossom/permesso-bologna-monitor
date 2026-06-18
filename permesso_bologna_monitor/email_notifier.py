from __future__ import annotations

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape

from permesso_bologna_monitor.constants import SMTP_TIMEOUT_SECONDS
from permesso_bologna_monitor.types import CheckResult, EmailSettings, QuesturaStatus

logger = logging.getLogger(__name__)


def result_subject(result: CheckResult) -> str:
    if result.status is QuesturaStatus.READY:
        return "Questura Bologna - Permit ready for pickup"
    if result.status is QuesturaStatus.NOT_READY:
        return "Questura Bologna - Permit not ready yet"
    return "Questura Bologna - Check permit result"


def status_label(result: CheckResult) -> str:
    if result.status is QuesturaStatus.READY:
        return "Positive result: the permit appears ready for pickup."
    if result.status is QuesturaStatus.NOT_READY:
        return "Negative result: the permit does not appear ready yet."
    return "Unknown result: a manual check is recommended."


def response_excerpt(text: str, limit: int = 1200) -> str:
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def send_email(
    settings: EmailSettings,
    *,
    subject: str,
    body_text: str,
    body_html: str,
) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.smtp_user
    message["To"] = settings.notify_email
    message.attach(MIMEText(body_text, "plain", "utf-8"))
    message.attach(MIMEText(body_html, "html", "utf-8"))

    logger.info("Sending email to %s", settings.notify_email)
    with smtplib.SMTP(
        settings.smtp_host,
        settings.smtp_port,
        timeout=SMTP_TIMEOUT_SECONDS,
    ) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(settings.smtp_user, settings.smtp_password)
        refused = server.sendmail(
            settings.smtp_user,
            [settings.notify_email],
            message.as_string(),
        )
        if refused:
            raise smtplib.SMTPException(f"SMTP refused recipients: {refused}")


def send_result_email(settings: EmailSettings, result: CheckResult) -> None:
    subject = result_subject(result)
    label = status_label(result)
    excerpt = response_excerpt(result.response_text)

    body_text = (
        f"{label}\n\n"
        f"Detail: {result.detail}\n"
        f"Checked URL: {result.checked_url}\n\n"
        "Response excerpt:\n"
        f"{excerpt}\n"
    )
    body_html = (
        f"<p><strong>{escape(label)}</strong></p>"
        f"<p>{escape(result.detail)}</p>"
        f'<p><a href="{escape(result.checked_url)}">Open Questura Bologna</a></p>'
        "<h3>Response excerpt</h3>"
        f"<pre>{escape(excerpt)}</pre>"
    )

    send_email(settings, subject=subject, body_text=body_text, body_html=body_html)
