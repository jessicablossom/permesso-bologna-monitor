from __future__ import annotations

import unittest
from unittest.mock import patch

from permesso_bologna_monitor.email_notifier import (
    response_excerpt,
    result_subject,
    send_result_email,
    status_label,
)
from permesso_bologna_monitor.types import CheckResult, QuesturaStatus
from tests.helpers import make_settings


def make_result(status: QuesturaStatus = QuesturaStatus.NOT_READY) -> CheckResult:
    return CheckResult(
        status=status,
        detail="Test detail",
        checked_url="https://www.questura.bologna.it/result",
        response_text="Questura response",
    )


class EmailNotifierTests(unittest.TestCase):
    def test_result_subject_matches_status(self) -> None:
        self.assertEqual(
            result_subject(make_result(QuesturaStatus.READY)),
            "Questura Bologna - Permit ready for pickup",
        )
        self.assertEqual(
            result_subject(make_result(QuesturaStatus.UNKNOWN)),
            "Questura Bologna - Check permit result",
        )

    def test_status_label_matches_status(self) -> None:
        self.assertIn("Negative", status_label(make_result(QuesturaStatus.NOT_READY)))
        self.assertIn("Positive", status_label(make_result(QuesturaStatus.READY)))

    def test_response_excerpt_truncates_long_text(self) -> None:
        excerpt = response_excerpt("abcde", limit=3)

        self.assertEqual(excerpt, "abc...")

    def test_send_result_email_builds_plain_and_html_bodies(self) -> None:
        settings = make_settings()
        result = make_result(QuesturaStatus.NOT_READY)

        with patch("permesso_bologna_monitor.email_notifier.send_email") as send_email:
            send_result_email(settings, result)

        send_email.assert_called_once()
        _, kwargs = send_email.call_args
        self.assertEqual(kwargs["subject"], "Questura Bologna - Permit not ready yet")
        self.assertIn("Test detail", kwargs["body_text"])
        self.assertIn("Questura response", kwargs["body_html"])


if __name__ == "__main__":
    unittest.main()
