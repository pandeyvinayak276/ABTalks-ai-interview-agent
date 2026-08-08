"""HTTP API for the ABTalks AI Interview Agent."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.breeth_memory import BreethMemory
from backend.data_loader import (
    Candidate as LoadedCandidate,
    CandidateMission,
    CandidateSignals,
    InterviewData,
    Member as LoadedMember,
    load_interview_data,
)
from backend.interview_planner import InterviewPlanner, PlannedQuestion


# ---------------------------------------------------------------------------
# API models
# ---------------------------------------------------------------------------


class Member(BaseModel):
    """Candidate profile fields supplied by the cohort candidate data."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    jobRole: str = Field(min_length=1)
    yearsExperience: int = Field(ge=0)
    education: str = Field(min_length=1)
    status: str = Field(min_length=1)


class Mission(BaseModel):
    """One curriculum mission in a candidate's learning history."""

    model_config = ConfigDict(extra="forbid")

    day: int = Field(ge=1)
    title: str = Field(min_length=1)
    passed: bool | None = None
    skipped: bool | None = None
    attempts: int | None = Field(default=None, ge=1)


class Signals(BaseModel):
    """Aggregate cohort engagement signals."""

    model_config = ConfigDict(extra="forbid")

    commitDays: int = Field(ge=0)
    missionsCompleted: int = Field(ge=0)
    missionsFirstTry: int = Field(ge=0)


class Candidate(BaseModel):
    """Candidate payload shape used by the supplied candidates data."""

    model_config = ConfigDict(extra="forbid")

    member: Member
    missions: list[Mission]
    signals: Signals


class InterviewRequest(BaseModel):
    """Start an interview with a candidate or continue it with a message."""

    model_config = ConfigDict(extra="forbid")

    sessionId: str = Field(min_length=1)
    candidate: Candidate | None = None
    message: str | None = None

    @model_validator(mode="after")
    def validate_interview_turn(self) -> "InterviewRequest":
        if self.candidate is None and self.message is None:
            raise ValueError(
                "Provide candidate to start an interview or message to continue one."
            )

        if self.candidate is not None and self.message is not None:
            raise ValueError("Provide either candidate or message, not both.")

        if self.message is not None and not self.message.strip():
            raise ValueError("message must not be blank.")

        return self


class Feedback(BaseModel):
    """Structured feedback returned after interview completion."""

    summary: str
    strengths: list[str]
    gaps: list[str]
    next: list[str]


class InterviewResponse(BaseModel):
    reply: str
    done: bool
    feedback: Feedback | None = None

# ---------------------------------------------------------------------------
# Internal interview state
# ---------------------------------------------------------------------------

@dataclass
class InterviewTurn:
    """One question-answer pair from the interview."""

    question: PlannedQuestion
    answer: str
    analysis: dict[str, Any]


@dataclass
class InterviewSession:
    candidate: LoadedCandidate
    planner: InterviewPlanner
    current_question: PlannedQuestion | None = None
    turns: list[InterviewTurn] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------


app = FastAPI(title="ABTalks AI Interview Agent")

sessions: dict[str, InterviewSession] = {}

breeth = BreethMemory()

try:
    interview_data: InterviewData = load_interview_data()
except Exception:
    interview_data = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Candidate conversion
# ---------------------------------------------------------------------------


def _to_loaded_candidate(candidate: Candidate) -> LoadedCandidate:
    """Convert API candidate into the planner's dataclass structure."""

    return LoadedCandidate(
        member=LoadedMember(
            id=candidate.member.id,
            name=candidate.member.name,
            job_role=candidate.member.jobRole,
            years_experience=candidate.member.yearsExperience,
            education=candidate.member.education,
            status=candidate.member.status,
        ),
        missions=tuple(
            CandidateMission(
                day=mission.day,
                title=mission.title,
                passed=mission.passed,
                skipped=mission.skipped,
                attempts=mission.attempts,
            )
            for mission in candidate.missions
        ),
        signals=CandidateSignals(
            commit_days=candidate.signals.commitDays,
            missions_completed=candidate.signals.missionsCompleted,
            missions_first_try=candidate.signals.missionsFirstTry,
        ),
    )


def _resolve_candidate(candidate: Candidate) -> LoadedCandidate:
    """Use canonical dataset candidate when available."""

    if interview_data is not None:
        loaded = interview_data.get_candidate(candidate.member.id)

        if loaded is not None:
            return loaded

    return _to_loaded_candidate(candidate)


# ---------------------------------------------------------------------------
# Adaptive interview length
# ---------------------------------------------------------------------------


def _calculate_interview_target(candidate: LoadedCandidate) -> int:
    """
    Determine an adaptive interview length between 8 and 13.

    Stronger engagement and deeper mission history can result in
    a longer interview.
    """

    target = 8

    completed_missions = candidate.signals.missions_completed
    commit_days = candidate.signals.commit_days
    first_try = candidate.signals.missions_first_try

    high_attempt_missions = sum(
        1
        for mission in candidate.missions
        if (
            mission.passed is True
            and mission.attempts is not None
            and mission.attempts >= 3
        )
    )

    if completed_missions >= 20:
        target += 1

    if commit_days >= 20:
        target += 1

    if completed_missions > 0:
        first_try_ratio = first_try / completed_missions

        if first_try_ratio >= 0.60:
            target += 1

    if high_attempt_missions >= 1:
        target += 1

    if high_attempt_missions >= 2:
        target += 1

    return min(target, 13)


# ---------------------------------------------------------------------------
# Breeth
# ---------------------------------------------------------------------------


def _search_breeth(question: PlannedQuestion) -> dict[str, Any]:
    """Retrieve relevant Breeth memory as context only."""

    if not breeth.enabled:
        return {
            "enabled": False,
            "results": [],
        }

    query = (
        f"Interview context for curriculum day {question.curriculum_day}. "
        f"Topic: {question.curriculum_topic}. "
        f"Objective: {question.objective}. "
        f"Difficulty: {question.difficulty}."
    )

    try:
        return breeth.search_memory(
            query=query,
            limit=5,
        )
    except Exception as exc:
        return {
            "enabled": True,
            "results": [],
            "error": str(exc),
        }


def _format_memory_context(memory: dict[str, Any]) -> str:
    """Convert Breeth search output into compact readable context."""

    if not memory.get("enabled"):
        return ""

    results = memory.get("results")

    if not results:
        return ""

    if isinstance(results, list):
        context_items: list[str] = []

        for index, result in enumerate(results[:3], start=1):
            if isinstance(result, str):
                text = result

            elif isinstance(result, dict):
                text = (
                    result.get("content")
                    or result.get("text")
                    or result.get("memory")
                    or result.get("snippet")
                    or json.dumps(
                        result,
                        ensure_ascii=False,
                    )
                )

            else:
                text = str(result)

            text = str(text).strip()

            if text:
                context_items.append(f"{index}. {text}")

        if context_items:
            return "\n".join(context_items)

    return json.dumps(
        memory,
        ensure_ascii=False,
    )[:2000]


# ---------------------------------------------------------------------------
# Question rendering
# ---------------------------------------------------------------------------


def _render_question(
    question: PlannedQuestion,
    memory_context: str = "",
) -> str:
    """Convert a deterministic plan into an interview question."""

    if question.is_follow_up and question.follow_up_instruction is not None:
        reply = (
            f"Let's go deeper into your previous answer about "
            f"**{question.curriculum_topic}**. "
            f"{question.follow_up_instruction.instruction} "
            f"Please explain your reasoning, discuss the trade-offs, "
            f"and give a concrete example."
        )

    elif question.difficulty == "deeper_probe":
        reply = (
            f"Let's go a little deeper into your experience with "
            f"**{question.curriculum_topic}**. "
            f"How would you approach a problem related to "
            f"**{question.objective}**? "
            f"Explain the design decisions you would make, the trade-offs "
            f"you would consider, and a concrete example from a realistic "
            f"engineering scenario."
        )

    else:
        reply = (
            f"Let's discuss **{question.curriculum_topic}**. "
            f"How would you approach a problem related to "
            f"**{question.objective}**? "
            f"Please explain your reasoning and, where possible, give a "
            f"concrete example."
        )

    if memory_context:
        reply += (
            "\n\nRelevant context from interview memory:\n"
            f"{memory_context}"
        )

    return reply


# ---------------------------------------------------------------------------
# Answer analysis
# ---------------------------------------------------------------------------


def _analyze_answer(
    answer: str,
    question: PlannedQuestion,
) -> dict[str, Any]:
    """Extract deterministic quality signals from one candidate answer."""

    normalized = answer.lower().strip()
    word_count = len(answer.split())

    technical_terms = [
        "because",
        "trade-off",
        "tradeoff",
        "example",
        "architecture",
        "design",
        "performance",
        "scalability",
        "latency",
        "security",
        "testing",
        "monitoring",
        "database",
        "api",
        "model",
        "embedding",
        "retrieval",
        "docker",
        "kubernetes",
        "vector",
        "cache",
    ]

    matched_terms = [
        term
        for term in technical_terms
        if term in normalized
    ]

    has_example = (
        "example" in normalized
        or "for instance" in normalized
        or "for example" in normalized
    )

    has_reasoning = (
        "because" in normalized
        or "therefore" in normalized
        or "so that" in normalized
        or "i would" in normalized
    )

    has_tradeoff = (
        "trade-off" in normalized
        or "tradeoff" in normalized
        or "pros and cons" in normalized
        or "downside" in normalized
    )

    if word_count >= 100 and len(matched_terms) >= 3:
        quality = "strong"
    elif word_count >= 50 and len(matched_terms) >= 2:
        quality = "good"
    elif word_count >= 25:
        quality = "adequate"
    else:
        quality = "brief"

    return {
        "word_count": word_count,
        "matched_terms": matched_terms,
        "has_example": has_example,
        "has_reasoning": has_reasoning,
        "has_tradeoff": has_tradeoff,
        "quality": quality,
        "topic": question.curriculum_topic,
        "objective": question.objective,
        "question_number": question.question_number,
        "difficulty": question.difficulty,
    }


# ---------------------------------------------------------------------------
# Adaptive follow-up decision
# ---------------------------------------------------------------------------


def _should_add_follow_up(
    answer_analysis: dict[str, Any],
    question: PlannedQuestion,
    planner: InterviewPlanner,
) -> bool:
    """Decide whether a strong core answer deserves deeper probing."""

    if question.is_follow_up:
        return False

    if planner.state.is_complete:
        return False

    if answer_analysis["quality"] != "strong":
        return False

    return True


# ---------------------------------------------------------------------------
# Candidate-specific feedback
# ---------------------------------------------------------------------------


def _build_feedback(
    session: InterviewSession,
) -> Feedback:
    """Build candidate-specific feedback from the completed interview."""

    turns = session.turns

    if not turns:
        return Feedback(
            summary="No interview answers were recorded.",
            strengths=[],
            gaps=["No candidate responses were available for evaluation."],
            next=["Complete the interview to receive technical feedback."],
        )

    completed = len(turns)

    covered_days = len(
        {
            turn.question.curriculum_day
            for turn in turns
        }
    )

    unique_topics = list(
        dict.fromkeys(
            turn.question.curriculum_topic
            for turn in turns
        )
    )

    # -----------------------------------------------------------------------
    # Classify answers
    # -----------------------------------------------------------------------

    strong_turns = [
        turn
        for turn in turns
        if turn.analysis["quality"] == "strong"
    ]

    good_turns = [
        turn
        for turn in turns
        if turn.analysis["quality"] == "good"
    ]

    adequate_turns = [
        turn
        for turn in turns
        if turn.analysis["quality"] == "adequate"
    ]

    brief_turns = [
        turn
        for turn in turns
        if turn.analysis["quality"] == "brief"
    ]

    example_turns = [
        turn
        for turn in turns
        if turn.analysis["has_example"]
    ]

    reasoning_turns = [
        turn
        for turn in turns
        if turn.analysis["has_reasoning"]
    ]

    tradeoff_turns = [
        turn
        for turn in turns
        if turn.analysis["has_tradeoff"]
    ]

    # -----------------------------------------------------------------------
    # Strengths
    # -----------------------------------------------------------------------

    strengths: list[str] = []

    # Rank topics by answer quality.
    topic_scores: dict[str, int] = {}

    quality_scores = {
        "strong": 4,
        "good": 3,
        "adequate": 2,
        "brief": 1,
    }

    for turn in turns:
        topic = turn.question.curriculum_topic
        quality = turn.analysis["quality"]

        topic_scores[topic] = (
            topic_scores.get(topic, 0)
            + quality_scores.get(quality, 0)
        )

    strongest_topics = sorted(
        topic_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )

    if strongest_topics and strongest_topics[0][1] >= 3:
        strengths.append(
            "Strongest demonstrated areas included "
            + ", ".join(
                topic
                for topic, _ in strongest_topics[:3]
            )
            + "."
        )

    if strong_turns:
        strengths.append(
            f"{len(strong_turns)} answer(s) demonstrated strong technical depth."
        )

    if good_turns:
        strengths.append(
            f"{len(good_turns)} answer(s) demonstrated solid technical understanding."
        )

    if example_turns:
        strengths.append(
            f"Concrete examples were used in {len(example_turns)} "
            "answer(s), showing practical understanding."
        )

    if reasoning_turns:
        strengths.append(
            f"Technical reasoning was clearly explained in "
            f"{len(reasoning_turns)} answer(s)."
        )

    if tradeoff_turns:
        strengths.append(
            f"Engineering trade-offs were discussed in "
            f"{len(tradeoff_turns)} answer(s)."
        )

    # Avoid an empty strengths section.
    if not strengths:
        strengths.append(
            "The candidate demonstrated participation across "
            f"{covered_days} curriculum area(s)."
        )

    # -----------------------------------------------------------------------
    # Gaps
    # -----------------------------------------------------------------------

    gaps: list[str] = []

    weaker_topics: list[str] = []

    for turn in turns:
        if turn.analysis["quality"] in {"adequate", "brief"}:
            topic = turn.question.curriculum_topic

            if topic not in weaker_topics:
                weaker_topics.append(topic)

    if weaker_topics:
        gaps.append(
            "The areas that need the most development are "
            + ", ".join(weaker_topics[:3])
            + "."
        )

    if brief_turns:
        gaps.append(
            f"{len(brief_turns)} answer(s) were relatively brief; "
            "more technical depth and concrete reasoning would strengthen them."
        )

    if not example_turns:
        gaps.append(
            "The candidate rarely used concrete engineering examples "
            "to support technical explanations."
        )

    if not reasoning_turns:
        gaps.append(
            "Technical answers should explain the reasoning behind "
            "design decisions more explicitly."
        )

    if not tradeoff_turns:
        gaps.append(
            "Architecture-level answers would benefit from discussing "
            "trade-offs such as scalability, performance, reliability, "
            "security, and cost."
        )

    if not gaps:
        gaps.append(
            "No major weakness was detected across the evaluated answers."
        )

    # -----------------------------------------------------------------------
    # Personalized next steps
    # -----------------------------------------------------------------------

    next_steps: list[str] = []

    if weaker_topics:
        next_steps.append(
            "Deepen your understanding of "
            + ", ".join(weaker_topics[:3])
            + " through hands-on implementation and system-design practice."
        )

    if brief_turns:
        next_steps.append(
            "Practice giving structured technical answers using "
            "concept → reasoning → example → trade-off."
        )

    if not example_turns:
        next_steps.append(
            "Practice connecting theoretical concepts to realistic "
            "engineering scenarios."
        )

    if not reasoning_turns:
        next_steps.append(
            "When answering technical questions, explain why you would "
            "choose an approach instead of only describing how it works."
        )

    if not tradeoff_turns:
        next_steps.append(
            "Practice evaluating scalability, performance, reliability, "
            "security, and cost when discussing system designs."
        )

    if not next_steps:
        next_steps.append(
            "Continue practicing concise explanations of technical "
            "design decisions using realistic engineering scenarios."
        )

    # Keep the feedback concise enough for an actual interview UI.
    next_steps = next_steps[:4]
    gaps = gaps[:4]
    strengths = strengths[:5]

    # -----------------------------------------------------------------------
    # Overall performance label
    # -----------------------------------------------------------------------

    if strong_turns and len(strong_turns) >= len(turns) * 0.5:
        overall_level = "strong technical performance"
    elif len(strong_turns) + len(good_turns) >= len(turns) * 0.6:
        overall_level = "solid technical performance"
    elif brief_turns > len(turns) * 0.4:
        overall_level = "developing technical performance"
    else:
        overall_level = "mixed technical performance"

    summary = (
        f"The candidate completed {completed} interview questions across "
        f"{covered_days} curriculum area(s), demonstrating {overall_level}. "
        f"Answer quality: {len(strong_turns)} strong, "
        f"{len(good_turns)} good, "
        f"{len(adequate_turns)} adequate, and "
        f"{len(brief_turns)} brief."
    )

    return Feedback(
        summary=summary,
        strengths=strengths,
        gaps=gaps,
        next=next_steps,
    )


# ---------------------------------------------------------------------------
# Interview endpoint
# ---------------------------------------------------------------------------


@app.post(
    "/api/interview",
    response_model=InterviewResponse,
    response_model_exclude_none=True,
)
def interview(
    request: InterviewRequest,
) -> InterviewResponse:
    """Initialize or continue an adaptive interview session."""

    # -----------------------------------------------------------------------
    # START INTERVIEW
    # -----------------------------------------------------------------------

    if request.candidate is not None:

        if request.sessionId in sessions:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "An interview session already exists for this sessionId."
                ),
            )

        if interview_data is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Interview data could not be loaded.",
            )

        try:
            loaded_candidate = _resolve_candidate(
                request.candidate
            )

            target_question_count = _calculate_interview_target(
                loaded_candidate
            )

            planner = InterviewPlanner(
                loaded_candidate,
                interview_data.curriculum,
                minimum_question_count=8,
                target_question_count=target_question_count,
                maximum_question_count=13,
            )

            first_question = planner.next_question()

        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Unable to initialize interview: {exc}",
            ) from exc

        if first_question is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="The interview planner could not provide a first question.",
            )

        session = InterviewSession(
            candidate=loaded_candidate,
            planner=planner,
            current_question=first_question,
        )

        sessions[request.sessionId] = session

        # Store candidate context in Breeth.
        if breeth.enabled:
            try:
                breeth.add_episode(
                    [
                        {
                            "role": "system",
                            "content": (
                                "Interview started. "
                                f"Candidate ID: {loaded_candidate.member.id}. "
                                f"Name: {loaded_candidate.member.name}. "
                                f"Role: {loaded_candidate.member.job_role}. "
                                f"Experience: "
                                f"{loaded_candidate.member.years_experience} years. "
                                f"Education: "
                                f"{loaded_candidate.member.education}. "
                                f"Adaptive target: "
                                f"{target_question_count} questions."
                            ),
                        }
                    ]
                )
            except Exception:
                pass

        memory = _search_breeth(first_question)

        memory_context = _format_memory_context(memory)

        return InterviewResponse(
            reply=_render_question(
                first_question,
                memory_context,
            ),
            done=False,
        )

    # -----------------------------------------------------------------------
    # CONTINUE INTERVIEW
    # -----------------------------------------------------------------------

    session = sessions.get(request.sessionId)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No interview session exists for this sessionId. "
                "Start with a candidate payload."
            ),
        )

    if session.current_question is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This interview has no active question.",
        )

    message = request.message.strip()

    current_question = session.current_question

    # Analyze the answer before changing planner state.
    answer_analysis = _analyze_answer(
        message,
        current_question,
    )

    # Store exact question-answer relationship.
    session.turns.append(
        InterviewTurn(
            question=current_question,
            answer=message,
            analysis=answer_analysis,
        )
    )

    # Store candidate answer in Breeth.
    if breeth.enabled:
        try:
            breeth.add_episode(
                [
                    {
                        "role": "user",
                        "content": (
                            f"Answer to question "
                            f"{current_question.question_number} "
                            f"about "
                            f"{current_question.curriculum_topic}: "
                            f"{message}"
                        ),
                    }
                ]
            )
        except Exception:
            pass

    # Complete the current question.
    try:
        interview_done = session.planner.complete_question(
            current_question.question_number
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    # -----------------------------------------------------------------------
    # INTERVIEW COMPLETE
    # -----------------------------------------------------------------------

    if interview_done:
        session.current_question = None

        return InterviewResponse(
            reply=(
                "Thank you. You have completed the interview. "
                "Here is your structured feedback."
            ),
            done=True,
            feedback=_build_feedback(session),
        )

    # -----------------------------------------------------------------------
    # OPTIONAL DEEPER FOLLOW-UP
    # -----------------------------------------------------------------------

    if _should_add_follow_up(
        answer_analysis,
        current_question,
        session.planner,
    ):
        try:
            session.planner.add_follow_up(
                previous_question_number=current_question.question_number,
                previous_answer_context=message,
            )
        except ValueError:
            pass

    # -----------------------------------------------------------------------
    # NEXT QUESTION
    # -----------------------------------------------------------------------

    next_question = session.planner.next_question()

    if next_question is None:
        session.current_question = None

        return InterviewResponse(
            reply=(
                "Thank you. The adaptive interview has been completed."
            ),
            done=True,
            feedback=_build_feedback(session),
        )

    session.current_question = next_question

    memory = _search_breeth(next_question)

    memory_context = _format_memory_context(memory)

    return InterviewResponse(
        reply=_render_question(
            next_question,
            memory_context,
        ),
        done=False,
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@app.get("/health")
def health() -> dict[str, str]:
    """Minimal local readiness check."""

    return {
        "status": "ok"
    }