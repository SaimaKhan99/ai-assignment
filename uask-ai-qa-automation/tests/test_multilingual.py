"""Multilingual behavior validation tests."""

from __future__ import annotations

from utils.language_utils import contains_arabic, detect_predominant_language, is_rtl_text
from validators.semantic_validator import SemanticValidator


def test_arabic_prompt_returns_response(chat_page, test_data):
    """Verify that an Arabic prompt returns a non-empty response."""
    query = test_data["arabic_queries"][0]
    response = chat_page.send_and_wait_for_response(query["prompt"])
    assert response.strip(), "Expected a non-empty Arabic response."


def test_arabic_response_contains_arabic_text(chat_page, test_data):
    """Verify that an Arabic prompt yields Arabic-script content."""
    query = test_data["arabic_queries"][0]
    response = chat_page.send_and_wait_for_response(query["prompt"])
    assert contains_arabic(response), f"Expected Arabic script in response: {response}"
    assert detect_predominant_language(response) == "ar"


def test_rtl_or_direction_support_for_arabic(chat_page, test_data):
    """Verify that Arabic rendering respects RTL direction when available."""
    query = test_data["arabic_queries"][1]
    response = chat_page.send_and_wait_for_response(query["prompt"])
    response_direction = chat_page.get_response_direction()
    input_direction = chat_page.get_input_direction()

    assert contains_arabic(response)
    assert response_direction in {"rtl", "ltr"}
    assert input_direction in {"rtl", "ltr"}
    assert response_direction == "rtl" or is_rtl_text(response)


def test_english_and_arabic_same_intent_are_reasonably_consistent(chat_page, test_data):
    """Verify that English and Arabic prompts for the same intent stay aligned."""
    english_query = test_data["english_queries"][0]
    arabic_query = test_data["arabic_queries"][0]

    english_response = chat_page.send_and_wait_for_response(english_query["prompt"])
    arabic_response = chat_page.send_and_wait_for_response(arabic_query["prompt"])

    consistency = SemanticValidator.are_multilingual_responses_consistent(
        english_response=english_response,
        arabic_response=arabic_response,
        english_intent=english_query["intent"],
        arabic_intent=arabic_query["intent"],
    )

    assert consistency["english_alignment"] >= 0.45
    assert consistency["arabic_alignment"] >= 0.45
    assert consistency["consistent"], f"Consistency check failed: {consistency}"
