from __future__ import annotations

import logging
import sys

from permesso_bologna_monitor.config import load_settings
from permesso_bologna_monitor.email_notifier import send_result_email
from permesso_bologna_monitor.questura import check_permesso


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main() -> int:
    configure_logging()
    try:
        settings = load_settings()
        result = check_permesso(settings)
        send_result_email(settings, result)
        print(f"Status: {result.status.value}")
        print(f"Detail: {result.detail}")
        return 0
    except Exception as error:
        logging.error("Questura check failed: %s", error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
