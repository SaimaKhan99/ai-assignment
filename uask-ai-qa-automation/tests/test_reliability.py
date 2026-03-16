"""Reliability and consistency validation tests."""

from __future__ import annotations

from validators.hallucination_detector import HallucinationDetector
from validators.response_validator import ResponseValidator
from validators.semantic_validator import SemanticValidator


def test_repeated_query_remains_stable_and_relevant(chat_page):
    """Verify that repeated queries remain relevant and broadly consistent."""
    prompt = "How can I apply for Emirates ID?"
    responses: list[str] = []

    for _ in range(3):
        response = chat_page.send_and_wait_for_response(prompt)
        assert ResponseValidator.is_non_empty(response)
        assert ResponseValidator.is_structurally_sound(response)
        assert not HallucinationDetector.is_likely_hallucinated(prompt, response)
        responses.append(response)

    similarity = SemanticValidator.pairwise_average_similarity(responses)
    assert similarity >= 0.55, f"Repeated-query consistency too low: {similarity:.3f}"
    assert chat_page.get_input_locator().is_enabled(), "Expected chat input to remain usable."
