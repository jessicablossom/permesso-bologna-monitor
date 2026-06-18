from __future__ import annotations

import unittest
from unittest.mock import patch

from permesso_bologna_monitor.cli import main
from permesso_bologna_monitor.types import CheckResult, QuesturaStatus
from tests.helpers import make_settings


class CliTests(unittest.TestCase):
    def test_main_returns_zero_when_check_and_email_succeed(self) -> None:
        settings = make_settings()
        check_result = CheckResult(
            status=QuesturaStatus.NOT_READY,
            detail="Not ready yet",
            checked_url="https://www.questura.bologna.it/result",
            response_text="Response",
        )

        with (
            patch("permesso_bologna_monitor.cli.load_settings", return_value=settings),
            patch("permesso_bologna_monitor.cli.check_permesso", return_value=check_result),
            patch("permesso_bologna_monitor.cli.send_result_email") as send_email,
        ):
            exit_code = main()

        self.assertEqual(exit_code, 0)
        send_email.assert_called_once_with(settings, check_result)

    def test_main_returns_one_when_check_fails(self) -> None:
        with (
            patch("permesso_bologna_monitor.cli.load_settings", side_effect=ValueError("boom")),
            self.assertLogs(level="ERROR"),
        ):
            exit_code = main()

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
