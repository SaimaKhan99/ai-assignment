"""Performance validation tests."""

from __future__ import annotations

from utils.config import STRICT_RESPONSE_TIME_SECONDS
from utils.performance_utils import measure_response_latency


def test_response_time_for_standard_query_is_under_threshold(chat_page):
    """Measure response latency for a representative public-service query."""
    _, latency = measure_response_latency(chat_page, "How do I renew my UAE visa?")
    assert latency <= STRICT_RESPONSE_TIME_SECONDS, (
        f"Response latency {latency:.2f}s exceeded configured threshold "
        f"{STRICT_RESPONSE_TIME_SECONDS:.2f}s"
    )
