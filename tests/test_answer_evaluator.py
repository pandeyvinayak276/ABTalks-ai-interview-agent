"""Tests for LLM answer evaluation and deterministic fallback behavior."""

import unittest
from unittest.mock import MagicMock, patch

import requests

from backend.answer_evaluator import AnswerEvaluator
from backend.interview_planner import PlannedQuestion


def _sample_question() -> PlannedQuestion:
    return PlannedQuestion(
        question_number=1,
        curriculum_day=7,
        curriculum_topic="Embeddings Explained",
        objective="Explain how embeddings represent text as vectors.",
        difficulty="core",
        reason_for_selection="Selected from completed mission history.",
        is_follow_up=False,
    )


def _valid_evaluation_json() -> str:
    return (
        '{"quality":"strong","has_example":true,"has_reasoning":true,'
        '"has_tradeoff":false,"matched_terms":["embedding","vector"]}'
    )


def _mock_llm_response(content: str) -> MagicMock:
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "choices": [{"message": {"content": content}}]
    }
    return mock_response


class AnswerEvaluatorTest(unittest.TestCase):
    def test_successful_llm_evaluation(self) -> None:
        evaluator = AnswerEvaluator(
            api_key="test-key",
            base_url="https://example.com/v1",
            model="test-model",
        )

        with patch(
            "backend.answer_evaluator.requests.post",
            return_value=_mock_llm_response(_valid_evaluation_json()),
        ) as post:
            result = evaluator.evaluate(
                "Embeddings map text to vectors for semantic search.",
                _sample_question(),
            )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.quality, "strong")
        self.assertTrue(result.has_example)
        self.assertTrue(result.has_reasoning)
        self.assertFalse(result.has_tradeoff)
        self.assertEqual(result.matched_terms, ["embedding", "vector"])
        post.assert_called_once()

    def test_valid_structured_response(self) -> None:
        evaluator = AnswerEvaluator(api_key="test-key")

        with patch(
            "backend.answer_evaluator.requests.post",
            return_value=_mock_llm_response(_valid_evaluation_json()),
        ):
            result = evaluator.evaluate("Detailed answer text.", _sample_question())

        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.quality, "strong")

    def test_missing_api_key_returns_none(self) -> None:
        evaluator = AnswerEvaluator(api_key="")

        with patch("backend.answer_evaluator.requests.post") as post:
            result = evaluator.evaluate("Answer text.", _sample_question())

        self.assertIsNone(result)
        post.assert_not_called()

    def test_provider_failure_returns_none(self) -> None:
        evaluator = AnswerEvaluator(api_key="test-key")

        with patch(
            "backend.answer_evaluator.requests.post",
            side_effect=requests.RequestException("provider unavailable"),
        ):
            result = evaluator.evaluate("Answer text.", _sample_question())

        self.assertIsNone(result)

    def test_invalid_json_returns_none(self) -> None:
        evaluator = AnswerEvaluator(api_key="test-key")

        with patch(
            "backend.answer_evaluator.requests.post",
            return_value=_mock_llm_response("not valid json"),
        ):
            result = evaluator.evaluate("Answer text.", _sample_question())

        self.assertIsNone(result)

    def test_invalid_quality_returns_none(self) -> None:
        evaluator = AnswerEvaluator(api_key="test-key")
        invalid_payload = (
            '{"quality":"excellent","has_example":true,"has_reasoning":true,'
            '"has_tradeoff":false,"matched_terms":["embedding"]}'
        )

        with patch(
            "backend.answer_evaluator.requests.post",
            return_value=_mock_llm_response(invalid_payload),
        ):
            result = evaluator.evaluate("Answer text.", _sample_question())

        self.assertIsNone(result)


class AnalyzeAnswerIntegrationTest(unittest.TestCase):
    def test_analyze_answer_uses_llm_when_available(self) -> None:
        from backend.main import _analyze_answer

        with patch("backend.main.answer_evaluator.evaluate") as evaluate:
            evaluate.return_value = type(
                "Result",
                (),
                {
                    "quality": "good",
                    "has_example": True,
                    "has_reasoning": False,
                    "has_tradeoff": True,
                    "matched_terms": ["cache"],
                },
            )()

            result = _analyze_answer(
                "I would cache embeddings because of latency trade-offs.",
                _sample_question(),
            )

        self.assertEqual(result["quality"], "good")
        self.assertTrue(result["has_example"])
        self.assertFalse(result["has_reasoning"])
        self.assertTrue(result["has_tradeoff"])
        self.assertEqual(result["matched_terms"], ["cache"])
        self.assertEqual(result["topic"], "Embeddings Explained")
        self.assertEqual(result["objective"], "Explain how embeddings represent text as vectors.")
        self.assertEqual(result["question_number"], 1)
        self.assertEqual(result["difficulty"], "core")
        self.assertGreater(result["word_count"], 0)

    def test_analyze_answer_falls_back_when_llm_unavailable(self) -> None:
        from backend.main import _analyze_answer

        answer = (
            "For example, I would use embeddings because they improve retrieval "
            "performance and scalability in a vector database architecture design. "
            "In production, I would monitor latency, test retrieval quality, and "
            "evaluate trade-offs between cache size and embedding dimensionality."
        )

        with patch("backend.main.answer_evaluator.evaluate", return_value=None):
            result = _analyze_answer(answer, _sample_question())

        self.assertIn(result["quality"], {"strong", "good", "adequate", "brief"})
        self.assertTrue(result["has_example"])
        self.assertTrue(result["has_reasoning"])
        self.assertGreaterEqual(result["word_count"], 25)
        self.assertEqual(result["topic"], "Embeddings Explained")


if __name__ == "__main__":
    unittest.main()
