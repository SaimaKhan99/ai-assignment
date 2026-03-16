"""Basic accessibility validation tests."""

from __future__ import annotations

import time


def test_input_has_accessible_presence(chat_page):
    """Verify that the input is discoverable to assistive technologies."""
    input_box = chat_page.get_input_locator()
    assert input_box.is_visible()

    tag_name = input_box.evaluate("element => element.tagName.toLowerCase()")
    aria_label = input_box.get_attribute("aria-label")
    aria_labelledby = input_box.get_attribute("aria-labelledby")
    placeholder = input_box.get_attribute("placeholder")

    assert tag_name in {"textarea", "input"}
    assert aria_label or aria_labelledby or placeholder


def test_send_button_keyboard_access(chat_page):
    """Verify that the send button can receive focus and be activated from keyboard flow."""
    send_button = chat_page.get_send_button_locator()
    prompt = "How do I renew my UAE visa?"
    chat_page.enter_message(prompt)
    send_button.focus()
    assert send_button.evaluate("element => document.activeElement === element")
    send_button.press("Enter")

    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and not chat_page.get_last_user_message():
        chat_page.page.wait_for_timeout(200)
    assert "visa" in chat_page.get_last_user_message().casefold()


def test_user_can_submit_with_keyboard_if_supported(chat_page):
    """Verify that pressing Enter in the textbox submits a message."""
    prompt = "How can I apply for Emirates ID?"
    previous_responses = chat_page.get_all_bot_responses()
    input_box = chat_page.get_input_locator()
    input_box.fill(prompt)
    input_box.press("Enter")

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if "Emirates ID".casefold() in chat_page.get_last_user_message().casefold():
            break
        chat_page.page.wait_for_timeout(200)

    assert "Emirates ID".casefold() in chat_page.get_last_user_message().casefold()

    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        current_responses = chat_page.get_all_bot_responses()
        if any(response not in previous_responses and len(response) > 20 for response in current_responses):
            break
        chat_page.page.wait_for_timeout(500)

    assert any(
        response not in previous_responses and len(response) > 20
        for response in chat_page.get_all_bot_responses()
    )
