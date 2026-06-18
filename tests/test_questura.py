from __future__ import annotations

import unittest

from permesso_bologna_monitor.constants import FIELD_PRACTICE_CODE, QUESTURA_FORM_ID
from permesso_bologna_monitor.questura import (
    build_payload,
    check_permesso,
    classify_response,
    extract_questura_form,
    parse_birth_date,
)
from permesso_bologna_monitor.types import QuesturaForm, QuesturaStatus
from tests.helpers import make_settings


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


class FakeSession:
    def __init__(self, form_html: str, result_html: str) -> None:
        self.form_html = form_html
        self.result_html = result_html
        self.post_url = ""
        self.post_data: dict[str, str] = {}

    def get(
        self,
        url: str,
        *,
        headers: dict[str, str],
        timeout: int,
    ) -> FakeResponse:
        return FakeResponse(self.form_html)

    def post(
        self,
        url: str,
        *,
        data: dict[str, str],
        headers: dict[str, str],
        timeout: int,
    ) -> FakeResponse:
        self.post_url = url
        self.post_data = data
        return FakeResponse(self.result_html)


class QuesturaTests(unittest.TestCase):
    def test_parse_birth_date_accepts_slashes_and_pads_parts(self) -> None:
        result = parse_birth_date("1/2/1980")

        self.assertEqual(result.day, "01")
        self.assertEqual(result.month, "02")
        self.assertEqual(result.year, "1980")

    def test_parse_birth_date_rejects_invalid_year(self) -> None:
        with self.assertRaisesRegex(ValueError, "four digits"):
            parse_birth_date("01/02/80")

    def test_extract_questura_form_reads_target_form_fields(self) -> None:
        html = f"""
        <form id="{QUESTURA_FORM_ID}" action="/node/2">
            <input name="form_build_id" value="abc">
            <input name="{FIELD_PRACTICE_CODE}" value="">
        </form>
        """

        form = extract_questura_form(html, "https://www.questura.bologna.it/start")

        self.assertEqual(form.action_url, "https://www.questura.bologna.it/node/2")
        self.assertEqual(form.fields["form_build_id"], "abc")

    def test_build_payload_fills_required_questura_fields(self) -> None:
        form = QuesturaForm(action_url="https://example.test", fields={"token": "abc"})

        payload = build_payload(form, " 08BO012345 ", "01-02-1980")

        self.assertEqual(payload["token"], "abc")
        self.assertEqual(payload["codraccomandata"], "")
        self.assertEqual(payload["codpratica"], "08BO012345")
        self.assertEqual(payload["dng"], "01")
        self.assertEqual(payload["dnm"], "02")
        self.assertEqual(payload["dna"], "1980")

    def test_classify_response_handles_accents(self) -> None:
        status, detail = classify_response("Il permesso di soggiorno e pronto per il ritiro")

        self.assertEqual(status, QuesturaStatus.READY)
        self.assertIn("ready", detail)

    def test_check_permesso_posts_form_and_returns_result(self) -> None:
        form_html = f"""
        <form id="{QUESTURA_FORM_ID}" action="/result">
            <input name="form_build_id" value="abc">
        </form>
        """
        result_html = "<main>Il permesso di soggiorno e pronto per il ritiro</main>"
        session = FakeSession(form_html, result_html)

        result = check_permesso(make_settings(), session=session)

        self.assertEqual(result.status, QuesturaStatus.READY)
        self.assertEqual(session.post_url, "https://www.questura.bologna.it/result")
        self.assertEqual(session.post_data["codpratica"], "08BO012345")


if __name__ == "__main__":
    unittest.main()
