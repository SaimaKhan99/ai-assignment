"""Layered response validation helpers."""

from __future__ import annotations

import re
from typing import Iterable


PUNCTUATION_ONLY_PATTERN = re.compile(r"^[\W_]+$")
STACKTRACE_PATTERN = re.compile(
    r"(traceback|exception:|stack trace|syntaxerror|referenceerror|typeerror)",
    re.IGNORECASE,
)
BROKEN_CONTENT_PATTERN = re.compile(
    r"(<script|</script>|undefined|null\b|nan\b|\[object object\])",
    re.IGNORECASE,
)
TRUNCATED_ENDING_PATTERN = re.compile(r"(\b(and|or|to|for|with|because)\s*$|[,:;]\s*$)")


class ResponseValidator:
    """Utility methods for validating live LLM responses."""

    @staticmethod
    def is_non_empty(response: str | None) -> bool:
        """Return True when the response is present and substantive."""
        if response is None:
            return False
        response = response.strip()
        if len(response) <= 20:
            return False
        return not PUNCTUATION_ONLY_PATTERN.fullmatch(response)

    @staticmethod
    def is_structurally_sound(response: str) -> bool:
        """Check for obvious rendering or backend failure artifacts."""
        if not response:
            return False
        if STACKTRACE_PATTERN.search(response):
            return False
        if BROKEN_CONTENT_PATTERN.search(response):
            return False
        if TRUNCATED_ENDING_PATTERN.search(response.strip()):
            return False
        return True

    @staticmethod
    def contains_expected_keywords(response: str, expected_keywords: Iterable[str]) -> bool:
        """Return True when at least one expected keyword appears in the response."""
        normalized = response.casefold()
        return any(keyword.casefold() in normalized for keyword in expected_keywords)

    @staticmethod
    def formatting_is_readable(response: str) -> bool:
        """Check that the response is readable and not collapsed into noise."""
        if not response:
            return False
        lines = [line.strip() for line in response.splitlines() if line.strip()]
        if not lines:
            return False
        longest_line = max(len(line) for line in lines)
        return longest_line < 1200

    @staticmethod
    def contains_fallback_markers(response: str, fallback_markers: Iterable[str]) -> bool:
        """Return True if the response looks like a system fallback."""
        normalized = response.casefold()
        return any(marker.casefold() in normalized for marker in fallback_markers)
