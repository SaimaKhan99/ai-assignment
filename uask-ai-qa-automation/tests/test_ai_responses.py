"""AI response validation tests."""

from __future__ import annotations

import pytest

from validators.hallucination_detector import HallucinationDetector
from validators.response_validator import ResponseValidator
from validators.semantic_validator import SemanticValidator


@pytest.mark.parametrize(
    "query_index",
    [0, 1, 2],
)
def test_common_english_public_service_queries(chat_page, test_data, query_index):
    """Validate standard public-service questions against layered AI checks."""
    query = test_data["english_queries"][query_index]
    response = chat_page.send_and_wait_for_response(query["prompt"])

    assert ResponseValidator.is_non_empty(response)
    assert ResponseValidator.is_structurally_sound(response)
    assert ResponseValidator.formatting_is_readable(response)
    assert not ResponseValidator.contains_fallback_markers(
        response,
        test_data["fallback_markers"],
    )
    assert not HallucinationDetector.is_likely_hallucinated(query["prompt"], response)


@pytest.mark.parametrize(
    "query_index",
    [0, 1, 2],
)
def test_response_contains_expected_keywords(chat_page, test_data, query_index):
    """Verify that each response reflects intent-related keywords."""
    query = test_data["english_queries"][query_index]
    response = chat_page.send_and_wait_for_response(query["prompt"])
    assert ResponseValidator.contains_expected_keywords(
        response,
        query["expected_keywords"],
    ), f"Expected at least one keyword from {query['expected_keywords']} in response: {response}"


@pytest.mark.parametrize(
    "query_index",
    [0, 1, 2],
)
def test_response_is_not_broken_or_empty(chat_page, test_data, query_index):
    """Verify that live responses are substantive and structurally sane."""
    query = test_data["english_queries"][query_index]
    response = chat_page.send_and_wait_for_response(query["prompt"])
    assert ResponseValidator.is_non_empty(response)
    assert ResponseValidator.is_structurally_sound(response)


@pytest.mark.parametrize(
    "query_index",
    [0, 1, 2],
)
def test_semantic_similarity_for_english_queries(chat_page, test_data, query_index):
    """Verify that responses remain semantically aligned with the intended topic."""
    query = test_data["english_queries"][query_index]
    response = chat_page.send_and_wait_for_response(query["prompt"])
    similarity = SemanticValidator.similarity(query["intent"], response)
    assert similarity >= 0.45, f"Semantic similarity too low: {similarity:.3f}"
