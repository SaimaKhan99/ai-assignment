"""Lightweight hallucination heuristics for public-service prompts."""

from __future__ import annotations

import re


OFF_TOPIC_PATTERN = re.compile(
    r"\b(joke|poem|song|once upon a time|funny story|knock knock|recipe)\b",
    re.IGNORECASE,
)
SUSPICIOUS_PHONE_PATTERN = re.compile(r"\b(?:\+?\d[\d\s-]{8,}\d)\b")
GOVERNMENT_SERVICE_PATTERN = re.compile(
    r"\b(uae|emirates|visa|id|license|permit|service|application|documents|authority|renew)\b",
    re.IGNORECASE,
)


class HallucinationDetector:
    """Heuristic detector for likely irrelevant or fabricated responses."""

    @staticmethod
    def detect(prompt: str, response: str) -> list[str]:
        """Return a list of hallucination indicators found in the response."""
        findings: list[str] = []
        prompt_is_service_question = bool(GOVERNMENT_SERVICE_PATTERN.search(prompt))

        if OFF_TOPIC_PATTERN.search(response):
            findings.append("off_topic_banter")

        phone_matches = SUSPICIOUS_PHONE_PATTERN.findall(response)
        if phone_matches and not any(number.startswith(("600", "800", "+971")) for number in phone_matches):
            findings.append("suspicious_phone_number")

        if prompt_is_service_question and not GOVERNMENT_SERVICE_PATTERN.search(response):
            findings.append("intent_not_reflected")

        if len(response.strip()) < 20:
            findings.append("too_short")

        return findings

    @staticmethod
    def is_likely_hallucinated(prompt: str, response: str) -> bool:
        """Return True if the response trips one or more strong heuristics."""
        findings = HallucinationDetector.detect(prompt, response)
        return any(flag in findings for flag in {"off_topic_banter", "intent_not_reflected"})
