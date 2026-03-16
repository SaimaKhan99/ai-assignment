"""Shared pytest fixtures and hooks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from pages.chatbot_page import ChatbotPage
from utils.config import DEFAULT_DESKTOP_VIEWPORT, DEFAULT_MOBILE_DEVICE, TEST_DATA_PATH
from utils.logger import get_logger
from utils.screenshot_utils import capture_page_screenshot


LOGGER = get_logger(__name__)


@pytest.fixture(scope="session")
def test_data() -> dict:
    """Load JSON-driven test data."""
    with Path(TEST_DATA_PATH).open(encoding="utf-8") as file_pointer:
        return json.load(file_pointer)


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    """Start the Playwright session."""
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Browser:
    """Create the shared Chromium browser instance."""
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture()
def context(browser: Browser) -> BrowserContext:
    """Create a desktop browser context."""
    context = browser.new_context(
        viewport=DEFAULT_DESKTOP_VIEWPORT,
        ignore_https_errors=True,
    )
    yield context
    context.close()


@pytest.fixture()
def page(context: BrowserContext) -> Page:
    """Create a desktop page."""
    page = context.new_page()
    page.set_default_timeout(30_000)
    yield page
    page.close()


@pytest.fixture()
def mobile_context(browser: Browser, playwright_instance: Playwright) -> BrowserContext:
    """Create a mobile device context."""
    device = playwright_instance.devices[DEFAULT_MOBILE_DEVICE]
    context = browser.new_context(**device, ignore_https_errors=True)
    yield context
    context.close()


@pytest.fixture()
def mobile_page(mobile_context: BrowserContext) -> Page:
    """Create a mobile page."""
    page = mobile_context.new_page()
    page.set_default_timeout(30_000)
    yield page
    page.close()


@pytest.fixture()
def chat_page(page: Page) -> ChatbotPage:
    """Open the chatbot on desktop and return its page object."""
    chatbot_page = ChatbotPage(page)
    LOGGER.info("Starting desktop chat fixture")
    chatbot_page.open_chatbot()
    chatbot_page.wait_for_chat_ready()
    return chatbot_page


@pytest.fixture()
def mobile_chat_page(mobile_page: Page) -> ChatbotPage:
    """Open the chatbot on mobile and return its page object."""
    chatbot_page = ChatbotPage(mobile_page)
    LOGGER.info("Starting mobile chat fixture")
    chatbot_page.open_chatbot()
    chatbot_page.wait_for_chat_ready()
    return chatbot_page


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Capture a screenshot on test failure and attach report sections."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or report.passed:
        return

    page = item.funcargs.get("page") or item.funcargs.get("mobile_page")
    if not page:
        return

    screenshot_path = capture_page_screenshot(page, item.name)
    LOGGER.error("Test failed: %s | Screenshot: %s", item.name, screenshot_path)
    item.add_report_section("call", "screenshot", str(screenshot_path))
    item.add_report_section("call", "log_file", "logs/test_execution.log")
