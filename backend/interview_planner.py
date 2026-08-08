"""Deterministic, curriculum-grounded interview planning."""

from __future__ import annotations

from dataclasses import dataclass, field

from backend.data_loader import Candidate, Curriculum, CurriculumDay


MINIMUM_QUESTION_COUNT = 8
MINIMUM_CURRICULUM_DAY_COVERAGE = 4
DEEPER_PROBE_ATTEMPTS = 3


@dataclass(frozen=True)
class FollowUpInstruction:
    """Context a future LLM layer can use to write a follow-up question."""

    previous_question_number: int
    previous_answer_context: str
    instruction: str


@dataclass(frozen=True)
class PlannedQuestion:
    """A structured question plan; no natural-language question is generated here."""

    question_number: int
    curriculum_day: int
    curriculum_topic: str
    objective: str
    difficulty: str
    reason_for_selection: str
    is_follow_up: bool
    follow_up_instruction: FollowUpInstruction | None = None


@dataclass
class InterviewState:
    """Mutable state for advancing one deterministic interview at a time."""

    member_id: str
    asked_questions: list[PlannedQuestion] = field(default_factory=list)
    covered_curriculum_days: set[int] = field(default_factory=set)
    current_question_number: int = 0
    minimum_question_count: int = MINIMUM_QUESTION_COUNT
    maximum_question_count: int = 10
    completed_question_numbers: set[int] = field(default_factory=set)
    is_complete: bool = False


@dataclass(frozen=True)
class _QuestionTemplate:
    curriculum_day: int
    curriculum_topic: str
    objective: str
    difficulty: str
    reason_for_selection: str
    is_follow_up: bool = False
    follow_up_instruction: FollowUpInstruction | None = None


class InterviewPlanner:
    """Plan and advance a deterministic interview for one supplied candidate."""

    def __init__(
        self,
        candidate: Candidate,
        curriculum: Curriculum,
        *,
        minimum_question_count: int = MINIMUM_QUESTION_COUNT,
        maximum_question_count: int = 10,
    ) -> None:
        if minimum_question_count < MINIMUM_QUESTION_COUNT:
            raise ValueError("minimum_question_count must be at least 8.")
        if maximum_question_count < minimum_question_count:
            raise ValueError("maximum_question_count cannot be below the minimum.")

        self._candidate = candidate
        self._curriculum_by_day = {item.day: item for item in curriculum.days}
        self.state = InterviewState(
            member_id=candidate.member.id,
            minimum_question_count=minimum_question_count,
            maximum_question_count=maximum_question_count,
        )
        self._core_questions = self._build_core_questions()
        self._follow_up_queue: list[_QuestionTemplate] = []
        self._followed_up_question_numbers: set[int] = set()

    @property
    def done(self) -> bool:
        """Whether the required question and curriculum-day coverage is complete."""

        return self.state.is_complete

    def next_question(self) -> PlannedQuestion | None:
        """Plan the next interview question and record it as asked."""

        if self.state.is_complete:
            return None
        if len(self.state.asked_questions) >= self.state.maximum_question_count:
            return None

        template = self._next_template()
        if template is None:
            return None

        question = PlannedQuestion(
            question_number=self.state.current_question_number + 1,
            curriculum_day=template.curriculum_day,
            curriculum_topic=template.curriculum_topic,
            objective=template.objective,
            difficulty=template.difficulty,
            reason_for_selection=template.reason_for_selection,
            is_follow_up=template.is_follow_up,
            follow_up_instruction=template.follow_up_instruction,
        )
        self.state.asked_questions.append(question)
        self.state.current_question_number = question.question_number
        return question

    def complete_question(self, question_number: int) -> bool:
        """Mark an asked question complete and return the updated completion state."""

        question = next(
            (item for item in self.state.asked_questions if item.question_number == question_number),
            None,
        )
        if question is None:
            raise ValueError("Only an asked question can be completed.")

        self.state.completed_question_numbers.add(question_number)
        self.state.covered_curriculum_days.add(question.curriculum_day)
        self.state.is_complete = (
            len(self.state.completed_question_numbers) >= self.state.minimum_question_count
            and len(self.state.covered_curriculum_days) >= MINIMUM_CURRICULUM_DAY_COVERAGE
        )
        return self.state.is_complete

    def add_follow_up(
        self,
        previous_question_number: int,
        previous_answer_context: str,
    ) -> FollowUpInstruction:
        """Queue one structured follow-up for an asked core question.

        This deliberately preserves answer context without generating question text.
        """

        if not previous_answer_context.strip():
            raise ValueError("previous_answer_context must not be blank.")
        if self.state.is_complete:
            raise ValueError("Cannot add a follow-up to a completed interview.")
        if previous_question_number in self._followed_up_question_numbers:
            raise ValueError("A follow-up is already queued for this question.")

        previous_question = next(
            (
                item
                for item in self.state.asked_questions
                if item.question_number == previous_question_number
            ),
            None,
        )
        if previous_question is None:
            raise ValueError("A follow-up requires a previously asked question.")
        if previous_question.is_follow_up:
            raise ValueError("Follow-ups may only be added to core questions.")

        instruction = FollowUpInstruction(
            previous_question_number=previous_question_number,
            previous_answer_context=previous_answer_context,
            instruction=(
                "Probe the candidate's explanation for understanding, trade-offs, "
                "and a concrete example related to the same curriculum objective."
            ),
        )
        self._follow_up_queue.append(
            _QuestionTemplate(
                curriculum_day=previous_question.curriculum_day,
                curriculum_topic=previous_question.curriculum_topic,
                objective=previous_question.objective,
                difficulty="follow_up",
                reason_for_selection=(
                    f"Follow up on question {previous_question_number} using the "
                    "candidate's supplied answer context."
                ),
                is_follow_up=True,
                follow_up_instruction=instruction,
            )
        )
        self._followed_up_question_numbers.add(previous_question_number)
        return instruction

    def advance_turn(self, completed_question_number: int) -> PlannedQuestion | None:
        """Complete one question and plan the next one for turn-by-turn use."""

        self.complete_question(completed_question_number)
        return self.next_question()

    def _next_template(self) -> _QuestionTemplate | None:
        if self._follow_up_queue:
            return self._follow_up_queue.pop(0)

        asked_core_questions = sum(
            not question.is_follow_up for question in self.state.asked_questions
        )
        if asked_core_questions < len(self._core_questions):
            return self._core_questions[asked_core_questions]
        return None

    def _build_core_questions(self) -> tuple[_QuestionTemplate, ...]:
        """Build distinct core questions from completed missions, then curriculum."""

        templates: list[_QuestionTemplate] = []
        selected_days: set[int] = set()

        for mission in self._candidate.missions:
            if mission.passed is not True or mission.day in selected_days:
                continue
            curriculum_day = self._curriculum_by_day.get(mission.day)
            if curriculum_day is None:
                continue
            templates.append(self._mission_template(curriculum_day, mission.attempts, mission.title))
            selected_days.add(mission.day)
            if len(templates) == self.state.minimum_question_count:
                return tuple(templates)

        for curriculum_day in sorted(self._curriculum_by_day.values(), key=lambda item: item.day):
            if curriculum_day.day in selected_days:
                continue
            templates.append(
                _QuestionTemplate(
                    curriculum_day=curriculum_day.day,
                    curriculum_topic=curriculum_day.title,
                    objective=_first_objective(curriculum_day),
                    difficulty="core",
                    reason_for_selection=(
                        "Selected from the supplied curriculum to preserve the required "
                        "interview breadth after prioritizing completed missions."
                    ),
                )
            )
            selected_days.add(curriculum_day.day)
            if len(templates) == self.state.minimum_question_count:
                return tuple(templates)

        raise ValueError("The supplied curriculum cannot provide the required eight questions.")

    @staticmethod
    def _mission_template(
        curriculum_day: CurriculumDay,
        attempts: int | None,
        mission_title: str,
    ) -> _QuestionTemplate:
        if attempts is not None and attempts >= DEEPER_PROBE_ATTEMPTS:
            difficulty = "deeper_probe"
            reason = (
                f"Candidate completed mission '{mission_title}' in {attempts} attempts; "
                "this is a deeper-probe opportunity."
            )
        elif attempts is not None:
            difficulty = "core"
            reason = (
                f"Candidate completed mission '{mission_title}' in {attempts} attempt(s), "
                "so this curriculum topic is prioritized."
            )
        else:
            difficulty = "core"
            reason = (
                f"Candidate completed mission '{mission_title}', so this curriculum topic "
                "is prioritized."
            )

        return _QuestionTemplate(
            curriculum_day=curriculum_day.day,
            curriculum_topic=curriculum_day.title,
            objective=_first_objective(curriculum_day),
            difficulty=difficulty,
            reason_for_selection=reason,
        )


def _first_objective(curriculum_day: CurriculumDay) -> str:
    if not curriculum_day.objectives:
        raise ValueError(f"Curriculum day {curriculum_day.day} has no objectives.")
    return curriculum_day.objectives[0]
