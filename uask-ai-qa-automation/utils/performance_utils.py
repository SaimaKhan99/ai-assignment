"""Performance measurement helpers."""

from __future__ import annotations

import time
from typing import Tuple

from pages.chatbot_page import ChatbotPage


def measure_response_latency(
    chatbot_page: ChatbotPage,
    message: str,
    timeout: int | None = None,
) -> Tuple[str, float]:
    """Send a message and return the response text plus latency in seconds."""
    start = time.perf_counter()
    response = chatbot_page.send_and_wait_for_response(message, timeout=timeout)
    latency = time.perf_counter() - start
    return response, latency
