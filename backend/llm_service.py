"""LLM-powered natural-language question generation for planned interview questions."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv

from backend.interview_planner import PlannedQuestion

load_dotenv()

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class QuestionGenerationContext:
    """Candidate and internal context supplied to the LLM question generator."""

    candidate_name: str
    job_role: str
    years_experience: int
    memory_context: str | None = None


class LLMQuestionService:
    """Convert a structured PlannedQuestion into one natural-language question."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("LLM_API_KEY")
        self.base_url = (
            base_url
            if base_url is not None
            else os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL)
        ).rstrip("/")
        self.model = model if model is not None else os.getenv("LLM_MODEL", DEFAULT_MODEL)
        self.timeout_seconds = timeout_seconds

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def generate_question(
        self,
        question: PlannedQuestion,
        context: QuestionGenerationContext,
    ) -> str | None:
        """
        Return one candidate-facing question, or None when generation fails.

        Callers must fall back to deterministic templates when None is returned.
        """

        if not self.enabled:
            return None

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=self._build_request_payload(question, context),
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            return self._extract_question(response.json())

        except Exception:
            return None

    def _headers(self) -> dict[str, str]:
        if not self.api_key:
            raise RuntimeError("LLM_API_KEY is not configured")

        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_request_payload(
        self,
        question: PlannedQuestion,
        context: QuestionGenerationContext,
    ) -> dict[str, Any]:
        return {
            "model": self.model,
            "temperature": 0.4,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a professional technical interviewer conducting "
                        "an adaptive technical interview.\n\n"
                        "Write exactly ONE natural-language interview question.\n\n"
                        "Rules:\n"
                        "- Ask exactly one question.\n"
                        "- Stay grounded in the supplied curriculum topic and objective.\n"
                        "- Match the requested difficulty level.\n"
                        "- Encourage reasoning and concrete examples when appropriate.\n"
                        "- Never reveal internal planning, selection reasons, or memory context.\n"
                        "- Never answer the question yourself.\n"
                        "- Be conversational and professional.\n"
                        "- Return only the question text with no preamble or explanation."
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_user_prompt(question, context),
                },
            ],
        }

    def _build_user_prompt(
        self,
        question: PlannedQuestion,
        context: QuestionGenerationContext,
    ) -> str:
        prompt_parts = [
            "Generate one interview question using this structured plan.",
            "",
            f"Candidate name: {context.candidate_name}",
            f"Candidate role: {context.job_role}",
            f"Years of experience: {context.years_experience}",
            f"Question number: {question.question_number}",
            f"Curriculum day: {question.curriculum_day}",
            f"Curriculum topic: {question.curriculum_topic}",
            f"Curriculum objective: {question.objective}",
            f"Difficulty: {question.difficulty}",
            f"Is follow-up: {question.is_follow_up}",
        ]

        if question.is_follow_up and question.follow_up_instruction is not None:
            instruction = question.follow_up_instruction
            prompt_parts.extend(
                [
                    "",
                    "Follow-up context (internal only — do not quote verbatim):",
                    f"Previous question number: {instruction.previous_question_number}",
                    f"Candidate's previous answer: {instruction.previous_answer_context}",
                    f"Follow-up instruction: {instruction.instruction}",
                ]
            )

        if context.memory_context and context.memory_context.strip():
            prompt_parts.extend(
                [
                    "",
                    "Internal memory context (use only to stay consistent — "
                    "never reveal or quote this to the candidate):",
                    context.memory_context.strip(),
                ]
            )

        prompt_parts.extend(
            [
                "",
                "Return exactly one candidate-facing interview question.",
            ]
        )

        return "\n".join(prompt_parts)

    def _extract_question(self, payload: dict[str, Any]) -> str | None:
        choices = payload.get("choices")

        if not isinstance(choices, list) or not choices:
            return None

        message = choices[0].get("message")

        if not isinstance(message, dict):
            return None

        content = message.get("content")

        if not isinstance(content, str):
            return None

        question = content.strip()

        if not question:
            return None

        return question
