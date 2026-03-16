"""UI behavior coverage for the U-Ask chatbot."""

from __future__ import annotations

from utils.logger import get_logger


LOGGER = get_logger(__name__)


def test_chat_page_loads(chat_page):
    """Verify that the main chatbot page loads successfully."""
    LOGGER.info("Running UI test: chat page loads")
    assert chat_page.is_widget_loaded(), "Expected chatbot widget to load successfully."


def test_chat_input_visible_and_enabled(chat_page):
    """Verify that the primary input is visible and ready for use."""
    input_box = chat_page.get_input_locator()
    assert input_box.is_visible(), "Expected the chatbot input textbox to be visible."
    assert input_box.is_enabled(), "Expected the chatbot input textbox to be enabled."


def test_user_can_send_message(chat_page):
    """Verify that a user can submit a message and see it in the transcript."""
    prompt = "How can I apply for Emirates ID?"
    chat_page.send_message(prompt)
    assert chat_page.get_last_user_message(), "Expected the user message to appear in the transcript."
    assert "Emirates ID".casefold() in chat_page.get_last_user_message().casefold()


def test_ai_response_is_rendered(chat_page):
    """Verify that a bot response is rendered after a user sends a message."""
    response = chat_page.send_and_wait_for_response("How do I renew my UAE visa?")
    assert response, "Expected a non-empty bot response to be rendered."


def test_input_clears_after_send(chat_page):
    """Verify that the input field is cleared after submitting a message."""
    chat_page.send_and_wait_for_response("How do I start a business in UAE?")
    assert chat_page.is_input_cleared(), "Expected the input textbox to clear after sending."


def test_chat_scroll_behavior_after_multiple_messages(chat_page):
    """Verify that the chat container remains scrollable after multiple messages."""
    prompts = [
        "How do I renew my UAE visa?",
        "What documents are needed for Emirates ID?",
        "How can I start a business in UAE?",
    ]
    for prompt in prompts:
        chat_page.send_and_wait_for_response(prompt)

    metrics = chat_page.scroll_chat()
    assert metrics["scrollable"], "Expected the chat area to become scrollable after multiple exchanges."
    assert metrics["after_scroll_top"] >= metrics["before_scroll_top"]


def test_mobile_view_chat_loads(mobile_chat_page):
    """Verify that the chat loads in a mobile viewport."""
    assert mobile_chat_page.is_widget_loaded(), "Expected the chatbot to load in mobile view."
    assert mobile_chat_page.get_input_locator().is_visible()
