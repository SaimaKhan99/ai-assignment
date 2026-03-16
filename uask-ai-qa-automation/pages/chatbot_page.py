"""Page object for the U-Ask chatbot."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, expect

from utils.config import BASE_URL, DEFAULT_TIMEOUT, RESPONSE_TIMEOUT_SECONDS
from utils.logger import get_logger
from utils.screenshot_utils import capture_page_screenshot


LocatorFactory = Callable[[], Locator]


class ChatbotPage:
    """Page object with resilient selector fallbacks for the live chatbot."""

    def __init__(self, page: Page, base_url: str = BASE_URL) -> None:
        self.page = page
        self.base_url = base_url
        self.logger = get_logger(__name__)

    def open_chatbot(self) -> None:
        """Open the U-Ask chatbot page."""
        self.logger.info("Opening chatbot page: %s", self.base_url)
        self.page.goto(self.base_url, wait_until="domcontentloaded", timeout=DEFAULT_TIMEOUT)

    def wait_for_chat_ready(self) -> None:
        """Wait until the core chat UI is available."""
        self.page.wait_for_load_state("networkidle", timeout=DEFAULT_TIMEOUT)
        self._first_visible_locator(
            [
                lambda: self.page.locator(".chatContainer"),
                lambda: self.page.locator("bbsf-textarea textarea"),
                lambda: self.page.locator(".question-container"),
                lambda: self.page.locator("sample-question-swiper"),
            ],
            timeout=DEFAULT_TIMEOUT,
        )
        expect(self._message_input()).to_be_visible(timeout=DEFAULT_TIMEOUT)

    def is_widget_loaded(self) -> bool:
        """Return True when the chat UI appears loaded."""
        try:
            return self._chat_container().is_visible() or self._message_input().is_visible()
        except PlaywrightTimeoutError:
            return False

    def enter_message(self, message: str) -> None:
        """Fill the message textbox."""
        input_box = self._message_input()
        expect(input_box).to_be_visible(timeout=DEFAULT_TIMEOUT)
        expect(input_box).to_be_enabled(timeout=DEFAULT_TIMEOUT)
        input_box.click()
        input_box.fill(message)
        self.logger.info("Prompt entered: %s", message)

    def click_send(self) -> None:
        """Click the send button using the most stable available locator."""
        send_button = self._send_button()
        expect(send_button).to_be_enabled(timeout=DEFAULT_TIMEOUT)
        send_button.click()

    def send_message(self, message: str) -> None:
        """Enter and send a chatbot message."""
        self.enter_message(message)
        try:
            self.click_send()
        except Exception:
            self._message_input().press("Enter")
        self.logger.info("Prompt submitted: %s", message)

    def send_and_wait_for_response(self, message: str, timeout: int | None = None) -> str:
        """Send a message and wait for a new bot response."""
        timeout_seconds = timeout or RESPONSE_TIMEOUT_SECONDS
        before_texts = self.get_all_bot_responses()
        self.send_message(message)
        deadline = time.monotonic() + timeout_seconds
        response = ""

        while time.monotonic() < deadline:
            self.page.wait_for_timeout(500)
            current_responses = self.get_all_bot_responses()
            new_responses = [item for item in current_responses if item not in before_texts]
            candidate = (new_responses[-1] if new_responses else current_responses[-1] if current_responses else "").strip()
            if len(candidate) > 20:
                response = candidate
                break

        if not response:
            raise AssertionError(
                f"Bot response was not detected within {timeout_seconds} seconds for prompt: {message}"
            )

        self.logger.info("Response received: %s", response)
        return response

    def get_last_bot_response(self) -> str:
        """Return the most recent bot response text."""
        responses = self.get_all_bot_responses()
        return responses[-1] if responses else ""

    def get_all_bot_responses(self) -> list[str]:
        """Return all visible bot response texts."""
        texts: list[str] = []
        locators = [
            self.page.locator(".chatContainer run-type-renderer"),
            self.page.locator(".chatContainer .auto-response-msg"),
            self.page.locator(".chatContainer [role='option'] .title"),
        ]
        for locator in locators:
            count = locator.count()
            for index in range(count):
                text = self._clean_text(locator.nth(index).inner_text())
                if text and text not in texts:
                    texts.append(text)
        return texts

    def get_last_user_message(self) -> str:
        """Return the last visible user message."""
        candidates = [
            self.page.locator(".chatContainer [role='option'] .title-user"),
            self.page.locator(".chatContainer .card-body-user .title-user"),
            self.page.locator(".chatContainer .title-user"),
        ]
        for locator in candidates:
            count = locator.count()
            if count:
                return self._clean_text(locator.nth(count - 1).inner_text())
        return ""

    def is_input_cleared(self) -> bool:
        """Return True when the message input is cleared after send."""
        return self._message_input().input_value().strip() == ""

    def scroll_chat(self) -> dict[str, int | bool]:
        """Scroll the chat container and return scroll metrics."""
        container = self._chat_container()
        metrics_before = container.evaluate(
            """element => ({
                scrollTop: element.scrollTop,
                scrollHeight: element.scrollHeight,
                clientHeight: element.clientHeight
            })"""
        )
        container.evaluate("element => element.scrollTo(0, element.scrollHeight)")
        metrics_after = container.evaluate(
            """element => ({
                scrollTop: element.scrollTop,
                scrollHeight: element.scrollHeight,
                clientHeight: element.clientHeight
            })"""
        )
        return {
            "before_scroll_top": metrics_before["scrollTop"],
            "after_scroll_top": metrics_after["scrollTop"],
            "scrollable": metrics_after["scrollHeight"] > metrics_after["clientHeight"],
        }

    def get_input_direction(self) -> str:
        """Return the input direction based on dir attribute or computed style."""
        return self._element_direction(self._message_input())

    def get_response_direction(self) -> str:
        """Return direction for the last response container."""
        response_locator = self._last_response_locator()
        return self._element_direction(response_locator)

    def is_error_fallback_shown(self, markers: list[str] | None = None) -> bool:
        """Return True when the last response looks like a fallback error."""
        response = self.get_last_bot_response().casefold()
        if not response:
            return False
        fallback_markers = markers or ["sorry", "please try again", "something went wrong"]
        return any(marker.casefold() in response for marker in fallback_markers)

    def capture_screenshot(self, file_name: str) -> Path:
        """Capture a named screenshot."""
        return capture_page_screenshot(self.page, file_name)

    def get_input_locator(self) -> Locator:
        """Expose the resolved message input locator to tests."""
        return self._message_input()

    def get_send_button_locator(self) -> Locator:
        """Expose the resolved send button locator to tests."""
        return self._send_button()

    def get_chat_container_locator(self) -> Locator:
        """Expose the resolved chat container locator to tests."""
        return self._chat_container()

    def start_new_chat(self) -> None:
        """Click the new chat action when available."""
        locator = self._first_visible_locator(
            [
                lambda: self.page.get_by_role("button", name="New Chat"),
                lambda: self.page.get_by_role("link", name="New Chat"),
                lambda: self.page.locator(".new-chat [role='button']"),
            ]
        )
        locator.click()

    def _message_input(self) -> Locator:
        return self._first_visible_locator(
            [
                lambda: self.page.locator("bbsf-textarea textarea"),
                lambda: self.page.locator(".question-container textarea"),
                lambda: self.page.get_by_placeholder("Please ask a question"),
                lambda: self.page.get_by_placeholder("اطرح سؤالاً"),
                lambda: self.page.get_by_role("textbox"),
                lambda: self.page.locator("textarea[name='conversation']"),
            ]
        )

    def _send_button(self) -> Locator:
        return self._first_visible_locator(
            [
                lambda: self.page.locator("button.send-question[type='submit']"),
                lambda: self.page.locator(".question-container button.send-question"),
                lambda: self.page.get_by_role("button", name="Send Message"),
                lambda: self.page.get_by_role("button", name="إرسال رسالة"),
                lambda: self.page.locator(".controls-card button[type='submit']"),
            ]
        )

    def _chat_container(self) -> Locator:
        return self._first_visible_locator(
            [
                lambda: self.page.locator(".chatContainer"),
                lambda: self.page.locator("[role='listbox'].chatContainer"),
                lambda: self.page.locator(".content-body [role='listbox']"),
            ]
        )

    def _last_response_locator(self) -> Locator:
        candidates = [
            self.page.locator(".chatContainer run-type-renderer"),
            self.page.locator(".chatContainer .auto-response-msg"),
            self.page.locator(".chatContainer [role='option'] .title"),
        ]
        for locator in candidates:
            count = locator.count()
            if count:
                return locator.nth(count - 1)
        raise AssertionError("Unable to locate any bot response container.")

    def _first_visible_locator(
        self,
        factories: list[LocatorFactory],
        timeout: int = 5000,
    ) -> Locator:
        deadline = time.monotonic() + (timeout / 1000)
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            for factory in factories:
                try:
                    locator = factory()
                    if locator.count() and locator.first.is_visible():
                        return locator.first
                except Exception as exc:  # noqa: BLE001
                    last_error = exc
            self.page.wait_for_timeout(200)
        if last_error:
            raise last_error
        raise AssertionError("No visible locator matched the configured fallback selectors.")

    @staticmethod
    def _clean_text(text: str | None) -> str:
        return " ".join((text or "").split()).strip()

    def _element_direction(self, locator: Locator) -> str:
        try:
            direction = locator.get_attribute("dir")
            if direction:
                return direction.lower()
            return locator.evaluate(
                "element => window.getComputedStyle(element).direction"
            ).lower()
        except Exception:  # noqa: BLE001
            html_dir = self.page.locator("html").get_attribute("dir")
            return (html_dir or "ltr").lower()
