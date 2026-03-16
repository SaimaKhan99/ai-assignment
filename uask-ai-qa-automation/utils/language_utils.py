"""Language and direction helpers."""

from __future__ import annotations

import re
from collections import Counter


ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+")
ENGLISH_PATTERN = re.compile(r"[A-Za-z]+")


def contains_arabic(text: str) -> bool:
    """Return True when the text contains Arabic script."""
    return bool(text and ARABIC_PATTERN.search(text))


def contains_english(text: str) -> bool:
    """Return True when the text contains English letters."""
    return bool(text and ENGLISH_PATTERN.search(text))


def detect_predominant_language(text: str) -> str:
    """Detect whether Arabic or English dominates the input text."""
    if not text:
        return "unknown"

    counts = Counter(
        {
            "ar": len(ARABIC_PATTERN.findall(text)),
            "en": len(ENGLISH_PATTERN.findall(text)),
        }
    )
    if counts["ar"] == counts["en"] == 0:
        return "unknown"
    return "ar" if counts["ar"] >= counts["en"] else "en"


def is_rtl_text(text: str) -> bool:
    """Infer right-to-left orientation from Arabic-dominant text."""
    return detect_predominant_language(text) == "ar"
