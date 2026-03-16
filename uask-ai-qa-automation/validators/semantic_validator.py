"""Semantic similarity validation using sentence-transformers."""

from __future__ import annotations

from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

from utils.config import SEMANTIC_SIMILARITY_THRESHOLD


class SemanticValidator:
    """Semantic comparison helper backed by all-MiniLM-L6-v2."""

    _model: SentenceTransformer | None = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Load the embedding model once per process."""
        if cls._model is None:
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._model

    @classmethod
    def similarity(cls, expected_intent: str, actual_response: str) -> float:
        """Compute cosine similarity between intent text and response text."""
        model = cls.get_model()
        embeddings = model.encode(
            [expected_intent, actual_response],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return float(np.dot(embeddings[0], embeddings[1]))

    @classmethod
    def pairwise_average_similarity(cls, responses: Iterable[str]) -> float:
        """Return the average pairwise semantic similarity for a set of responses."""
        response_list = [response for response in responses if response and response.strip()]
        if len(response_list) < 2:
            return 1.0

        model = cls.get_model()
        embeddings = model.encode(
            response_list,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        scores: list[float] = []
        for index, left in enumerate(embeddings):
            for right in embeddings[index + 1 :]:
                scores.append(float(np.dot(left, right)))
        return float(np.mean(scores)) if scores else 1.0

    @classmethod
    def meets_threshold(
        cls,
        expected_intent: str,
        actual_response: str,
        threshold: float = SEMANTIC_SIMILARITY_THRESHOLD,
    ) -> bool:
        """Convenience check for response-to-intent semantic similarity."""
        return cls.similarity(expected_intent, actual_response) >= threshold

    @classmethod
    def are_multilingual_responses_consistent(
        cls,
        english_response: str,
        arabic_response: str,
        english_intent: str,
        arabic_intent: str,
        threshold: float = SEMANTIC_SIMILARITY_THRESHOLD,
    ) -> dict[str, float | bool]:
        """Assess cross-language consistency with direct and self-intent scores."""
        english_alignment = cls.similarity(english_intent, english_response)
        arabic_alignment = cls.similarity(arabic_intent, arabic_response)
        direct_similarity = cls.similarity(english_response, arabic_response)

        consistent = (
            english_alignment >= threshold
            and arabic_alignment >= threshold
            and (direct_similarity >= 0.20 or min(english_alignment, arabic_alignment) >= threshold)
        )
        return {
            "english_alignment": english_alignment,
            "arabic_alignment": arabic_alignment,
            "direct_similarity": direct_similarity,
            "consistent": consistent,
        }
