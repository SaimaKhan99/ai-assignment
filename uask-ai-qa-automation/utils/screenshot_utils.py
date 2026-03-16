"""Screenshot helpers."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page

from utils.config import SCREENSHOT_DIR


def build_screenshot_path(test_name: str) -> Path:
    """Build a timestamped screenshot path for a given test."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_test_name = "".join(char if char.isalnum() or char in {"_", "-"} else "_" for char in test_name)
    return SCREENSHOT_DIR / f"{safe_test_name}_{timestamp}.png"


def capture_page_screenshot(page: Page, test_name: str) -> Path:
    """Capture and persist a screenshot for the current page."""
    path = build_screenshot_path(test_name)
    page.screenshot(path=str(path), full_page=True)
    return path
