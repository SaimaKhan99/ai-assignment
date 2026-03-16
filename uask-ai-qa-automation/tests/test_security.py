"""Security and adversarial input validation tests."""

from __future__ import annotations

from validators.response_validator import ResponseValidator
from validators.security_validator import SecurityValidator


def test_script_injection_is_safely_handled(chat_page, test_data):
    """Verify that script-tag input is handled safely and does not execute."""
    dialogs: list[str] = []

    def handle_dialog(dialog) -> None:
        dialogs.append(dialog.message)
        dialog.dismiss()

    chat_page.page.on("dialog", handle_dialog)

    payload = test_data["security_inputs"][0]["prompt"]
    response = chat_page.send_and_wait_for_response(payload)
    user_message = chat_page.get_last_user_message()

    assert not dialogs, f"Unexpected browser dialog triggered by payload: {dialogs}"
    assert SecurityValidator.is_harmless_rendering(user_message, response)


def test_sql_like_input_is_safely_handled(chat_page, test_data):
    """Verify that SQL-like payloads do not expose backend failure details."""
    payload = test_data["security_inputs"][1]["prompt"]
    response = chat_page.send_and_wait_for_response(payload)

    assert ResponseValidator.is_non_empty(response)
    assert SecurityValidator.is_sql_payload_handled_safely(response)


def test_prompt_injection_is_resisted(chat_page, test_data):
    """Verify that malicious instruction override attempts do not derail the assistant."""
    payload = test_data["security_inputs"][2]["prompt"]
    response = chat_page.send_and_wait_for_response(payload)

    assert SecurityValidator.is_prompt_injection_resisted(
        response
    ), f"Prompt injection looked successful: {response}"


def test_response_does_not_render_raw_html(chat_page):
    """Verify that suspicious HTML is not rendered back as raw executable markup."""
    payload = "<img src=x onerror=alert(1)> How do I renew my UAE visa?"
    response = chat_page.send_and_wait_for_response(payload)

    assert not SecurityValidator.contains_raw_html(response)
    assert not SecurityValidator.contains_script_markup(response)
