"""Tests for LLM question generation and deterministic fallback behavior."""

import unittest
from unittest.mock import MagicMock, patch

import requests

from backend.interview_planner import FollowUpInstruction, PlannedQuestion
from backend.llm_service import LLMQuestionService, QuestionGenerationContext


def _sample_question(*, is_follow_up: bool = False) -> PlannedQuestion:
    follow_up_instruction = None

    if is_follow_up:
        follow_up_instruction = FollowUpInstruction(
            previous_question_number=1,
            previous_answer_context="I would use a vector database for retrieval.",
            instruction=(
                "Probe the candidate's explanation for understanding, "
                "trade-offs, and a concrete example related to the same "
                "curriculum objective."
            ),
        )

    return PlannedQuestion(
        question_number=2 if is_follow_up else 1,
        curriculum_day=7,
        curriculum_topic="Embeddings Explained",
        objective="Explain how embeddings represent text as vectors.",
        difficulty="follow_up" if is_follow_up else "core",
        reason_for_selection="Selected from completed mission history.",
        is_follow_up=is_follow_up,
        follow_up_instruction=follow_up_instruction,
    )


def _sample_context() -> QuestionGenerationContext:
    return QuestionGenerationContext(
        candidate_name="Sarah Johnson",
        job_role="Senior Data Engineer",
        years_experience=9,
        memory_context="Internal note about prior retrieval discussion.",
    )


class LLMQuestionServiceTest(unittest.TestCase):
    def test_successful_generation(self) -> None:
        service = LLMQuestionService(
            api_key="test-key",
            base_url="https://example.com/v1",
            model="test-model",
        )
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": (
                            "Can you walk me through how you would explain "
                            "embeddings to a teammate?"
                        )
                    }
                }
            ]
        }

        with patch("backend.llm_service.requests.post", return_value=mock_response) as post:
            result = service.generate_question(
                _sample_question(),
                _sample_context(),
            )

        self.assertEqual(
            result,
            "Can you walk me through how you would explain embeddings to a teammate?",
        )
        post.assert_called_once()

        request_json = post.call_args.kwargs["json"]
        user_prompt = request_json["messages"][1]["content"]

        self.assertIn("Embeddings Explained", user_prompt)
        self.assertIn("Internal memory context", user_prompt)
        self.assertNotIn("Internal note about prior retrieval discussion.", result or "")

    def test_missing_api_key_returns_none(self) -> None:
        service = LLMQuestionService(api_key="")

        with patch("backend.llm_service.requests.post") as post:
            result = service.generate_question(
                _sample_question(),
                _sample_context(),
            )

        self.assertIsNone(result)
        post.assert_not_called()

    def test_provider_failure_returns_none(self) -> None:
        service = LLMQuestionService(api_key="test-key")

        with patch(
            "backend.llm_service.requests.post",
            side_effect=requests.RequestException("provider unavailable"),
        ):
            result = service.generate_question(
                _sample_question(),
                _sample_context(),
            )

        self.assertIsNone(result)

    def test_empty_response_returns_none(self) -> None:
        service = LLMQuestionService(api_key="test-key")
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "   "}}]
        }

        with patch("backend.llm_service.requests.post", return_value=mock_response):
            result = service.generate_question(
                _sample_question(),
                _sample_context(),
            )

        self.assertIsNone(result)


class QuestionRenderingIntegrationTest(unittest.TestCase):
    def test_render_question_uses_llm_when_available(self) -> None:
        from backend.main import _render_question

        with patch("backend.main.llm_service.generate_question") as generate:
            generate.return_value = "LLM-generated interview question?"

            result = _render_question(
                _sample_question(),
                candidate_name="Sarah Johnson",
                job_role="Senior Data Engineer",
                years_experience=9,
            )

        self.assertEqual(result, "LLM-generated interview question?")

    def test_render_question_falls_back_when_llm_unavailable(self) -> None:
        from backend.main import _render_question

        with patch("backend.main.llm_service.generate_question", return_value=None):
            result = _render_question(
                _sample_question(),
                candidate_name="Sarah Johnson",
                job_role="Senior Data Engineer",
                years_experience=9,
            )

        self.assertIn("Embeddings Explained", result)
        self.assertIn("Explain how embeddings represent text as vectors.", result)

    def test_render_question_follow_up_falls_back_with_instruction(self) -> None:
        from backend.main import _render_question

        with patch("backend.main.llm_service.generate_question", return_value=None):
            result = _render_question(
                _sample_question(is_follow_up=True),
                candidate_name="Sarah Johnson",
                job_role="Senior Data Engineer",
                years_experience=9,
            )

        self.assertIn("Embeddings Explained", result)
        self.assertIn("Probe the candidate's explanation", result)


if __name__ == "__main__":
    unittest.main()
