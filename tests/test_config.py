from __future__ import annotations

import os
import tempfile
import unittest

from permesso_bologna_monitor.config import load_settings, load_smtp_settings


CONFIG_ENV_KEYS = (
    "GITHUB_ACTIONS",
    "NOTIFY_EMAIL",
    "QUESTURA_BIRTH_DATE",
    "QUESTURA_PRACTICE_CODE",
    "QUESTURA_URL",
    "SMTP_HOST",
    "SMTP_PASSWORD",
    "SMTP_PORT",
    "SMTP_USER",
    "TIMEZONE",
)


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.previous_env = {key: os.environ.get(key) for key in CONFIG_ENV_KEYS}
        for key in CONFIG_ENV_KEYS:
            os.environ.pop(key, None)

    def tearDown(self) -> None:
        for key, value in self.previous_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_load_settings_reads_required_env_and_defaults(self) -> None:
        os.environ.update(
            {
                "QUESTURA_PRACTICE_CODE": "08BO012345",
                "QUESTURA_BIRTH_DATE": "01/02/1980",
                "SMTP_USER": "sender@test.com",
                "SMTP_PASSWORD": "app password",
            }
        )

        with tempfile.NamedTemporaryFile() as env_file:
            settings = load_settings(env_file.name)

        self.assertEqual(settings.questura_url, "https://www.questura.bologna.it/node/2")
        self.assertEqual(settings.timezone, "Europe/Rome")
        self.assertEqual(settings.notify_email, "sender@test.com")
        self.assertEqual(settings.smtp_password, "apppassword")

    def test_load_smtp_settings_rejects_missing_github_secrets(self) -> None:
        os.environ["GITHUB_ACTIONS"] = "true"

        with self.assertRaisesRegex(ValueError, "Missing GitHub Actions secrets"):
            load_smtp_settings()

    def test_load_smtp_settings_rejects_invalid_notify_email(self) -> None:
        os.environ.update(
            {
                "SMTP_USER": "sender@test.com",
                "SMTP_PASSWORD": "secret",
                "NOTIFY_EMAIL": "invalid-email",
            }
        )

        with self.assertRaisesRegex(ValueError, "Invalid NOTIFY_EMAIL"):
            load_smtp_settings()


if __name__ == "__main__":
    unittest.main()
