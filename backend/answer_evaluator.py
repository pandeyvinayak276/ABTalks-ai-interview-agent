"""LLM-powered answer evaluation for interview responses."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv

from backend.interview_planner import PlannedQuestion

load_dotenv()

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT_SECONDS = 15

ALLOWED_QUALITY_VALUES = frozenset({"strong", "good", "adequate", "brief"})


@dataclass(frozen=True)
class AnswerEvaluationResult:
    """LLM-derived answer signals merged into the full analysis dictionary."""

    quality: str
    has_example: bool
    has_reasoning: bool
    has_tradeoff: bool
    matched_terms: list[str]


class AnswerEvaluator:
    """Evaluate a candidate answer against a planned interview question."""

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

    def evaluate(
        self,
        answer: str,
        question: PlannedQuestion,
    ) -> AnswerEvaluationResult | None:
        """
        Return validated LLM evaluation signals, or None when evaluation fails.

        Callers must fall back to deterministic heuristics when None is returned.
        """

        if not self.enabled:
            return None

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=self._build_request_payload(answer, question),
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            content = self._extract_content(response.json())

            if content is None:
                return None

            return self._parse_evaluation(content)

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
        answer: str,
        question: PlannedQuestion,
    ) -> dict[str, Any]:
        return {
            "model": self.model,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a professional technical interviewer evaluating "
                        "a candidate's answer.\n\n"
                        "Judge the answer against the supplied question, curriculum "
                        "objective, and difficulty.\n\n"
                        "Evaluate:\n"
                        "- technical correctness and depth\n"
                        "- whether the answer is brief, adequate, good, or strong\n"
                        "- whether the candidate provided a concrete example\n"
                        "- whether the candidate explained their reasoning\n"
                        "- whether the candidate discussed engineering trade-offs\n"
                        "- relevant technical terms actually present in the answer\n\n"
                        "Rules:\n"
                        "- Return JSON only with no markdown or explanation.\n"
                        "- Use exactly these quality values: strong, good, adequate, brief.\n"
                        "- Never invent information not present in the answer.\n"
                        "- matched_terms must list technical terms found in the answer.\n\n"
                        "JSON schema:\n"
                        "{\n"
                        '  "quality": "strong|good|adequate|brief",\n'
                        '  "has_example": true,\n'
                        '  "has_reasoning": true,\n'
                        '  "has_tradeoff": false,\n'
                        '  "matched_terms": ["term1", "term2"]\n'
                        "}"
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_user_prompt(answer, question),
                },
            ],
        }

    def _build_user_prompt(
        self,
        answer: str,
        question: PlannedQuestion,
    ) -> str:
        prompt_parts = [
            "Evaluate this candidate answer.",
            "",
            f"Curriculum topic: {question.curriculum_topic}",
            f"Curriculum objective: {question.objective}",
            f"Difficulty: {question.difficulty}",
            f"Question number: {question.question_number}",
            f"Is follow-up: {question.is_follow_up}",
            "",
            "Candidate answer:",
            answer.strip(),
        ]

        return "\n".join(prompt_parts)

    def _extract_content(self, payload: dict[str, Any]) -> str | None:
        choices = payload.get("choices")

        if not isinstance(choices, list) or not choices:
            return None

        message = choices[0].get("message")

        if not isinstance(message, dict):
            return None

        content = message.get("content")

        if not isinstance(content, str):
            return None

        text = content.strip()

        if not text:
            return None

        return text

    def _parse_evaluation(self, content: str) -> AnswerEvaluationResult | None:
        payload = self._load_json_object(content)

        if payload is None:
            return None

        return self._validate_evaluation(payload)

    def _load_json_object(self, content: str) -> dict[str, Any] | None:
        try:
            parsed = json.loads(content)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:
            pass

        fenced_match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```",
            content,
            flags=re.DOTALL,
        )

        if fenced_match:
            try:
                parsed = json.loads(fenced_match.group(1))

                if isinstance(parsed, dict):
                    return parsed

            except json.JSONDecodeError:
                return None

        object_match = re.search(r"\{.*\}", content, flags=re.DOTALL)

        if object_match:
            try:
                parsed = json.loads(object_match.group(0))

                if isinstance(parsed, dict):
                    return parsed

            except json.JSONDecodeError:
                return None

        return None

    def _validate_evaluation(
        self,
        payload: dict[str, Any],
    ) -> AnswerEvaluationResult | None:
        quality = payload.get("quality")

        if not isinstance(quality, str) or quality not in ALLOWED_QUALITY_VALUES:
            return None

        has_example = payload.get("has_example")

        if not isinstance(has_example, bool):
            return None

        has_reasoning = payload.get("has_reasoning")

        if not isinstance(has_reasoning, bool):
            return None

        has_tradeoff = payload.get("has_tradeoff")

        if not isinstance(has_tradeoff, bool):
            return None

        matched_terms = payload.get("matched_terms")

        if not isinstance(matched_terms, list):
            return None

        normalized_terms: list[str] = []

        for term in matched_terms:
            if not isinstance(term, str):
                return None

            cleaned = term.strip()

            if cleaned:
                normalized_terms.append(cleaned)

        return AnswerEvaluationResult(
            quality=quality,
            has_example=has_example,
            has_reasoning=has_reasoning,
            has_tradeoff=has_tradeoff,
            matched_terms=normalized_terms,
        )
