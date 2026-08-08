"""Read-only access to the supplied ABTalks curriculum and candidate data."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"


@dataclass(frozen=True)
class CurriculumModule:
    n: int
    title: str
    days: tuple[int, ...]


@dataclass(frozen=True)
class CurriculumDay:
    day: int
    title: str
    type: str
    tools: tuple[str, ...]
    objectives: tuple[str, ...]


@dataclass(frozen=True)
class Curriculum:
    cohort: str
    modules: tuple[CurriculumModule, ...]
    days: tuple[CurriculumDay, ...]


@dataclass(frozen=True)
class Member:
    id: str
    name: str
    job_role: str
    years_experience: int
    education: str
    status: str


@dataclass(frozen=True)
class CandidateMission:
    day: int
    title: str
    passed: bool | None
    skipped: bool | None
    attempts: int | None


@dataclass(frozen=True)
class CandidateSignals:
    commit_days: int
    missions_completed: int
    missions_first_try: int


@dataclass(frozen=True)
class Candidate:
    member: Member
    missions: tuple[CandidateMission, ...]
    signals: CandidateSignals


@dataclass(frozen=True)
class InterviewData:
    """Loaded data with lookup helpers for the future interview engine."""

    curriculum: Curriculum
    candidates: tuple[Candidate, ...]

    def get_candidate(self, member_id: str) -> Candidate | None:
        """Return a candidate by their supplied member ID, if present."""

        return next(
            (candidate for candidate in self.candidates if candidate.member.id == member_id),
            None,
        )

    def get_curriculum_day(self, day: int) -> CurriculumDay | None:
        """Return curriculum information for a day number, if present."""

        return next((item for item in self.curriculum.days if item.day == day), None)


def load_curriculum(path: Path | None = None) -> Curriculum:
    """Load ``curriculum.json`` into typed, immutable structures."""

    source = path or DATA_DIRECTORY / "curriculum.json"
    with source.open(encoding="utf-8") as file:
        raw = json.load(file)

    return Curriculum(
        cohort=raw["cohort"],
        modules=tuple(
            CurriculumModule(
                n=module["n"],
                title=module["title"],
                days=tuple(module["days"]),
            )
            for module in raw["modules"]
        ),
        days=tuple(
            CurriculumDay(
                day=item["day"],
                title=item["title"],
                type=item["type"],
                tools=tuple(item["tools"]),
                objectives=tuple(item["objectives"]),
            )
            for item in raw["days"]
        ),
    )


def load_candidates(path: Path | None = None) -> tuple[Candidate, ...]:
    """Load ``candidates.json`` into typed, immutable structures."""

    source = path or DATA_DIRECTORY / "candidates.json"
    with source.open(encoding="utf-8") as file:
        raw = json.load(file)

    return tuple(_to_candidate(candidate) for candidate in raw["candidates"])


def load_interview_data(data_directory: Path | None = None) -> InterviewData:
    """Load both supplied data files from a directory without modifying them."""

    directory = data_directory or DATA_DIRECTORY
    return InterviewData(
        curriculum=load_curriculum(directory / "curriculum.json"),
        candidates=load_candidates(directory / "candidates.json"),
    )


def _to_candidate(raw: dict[str, Any]) -> Candidate:
    member = raw["member"]
    signals = raw["signals"]
    return Candidate(
        member=Member(
            id=member["id"],
            name=member["name"],
            job_role=member["jobRole"],
            years_experience=member["yearsExperience"],
            education=member["education"],
            status=member["status"],
        ),
        missions=tuple(
            CandidateMission(
                day=mission["day"],
                title=mission["title"],
                passed=mission.get("passed"),
                skipped=mission.get("skipped"),
                attempts=mission.get("attempts"),
            )
            for mission in raw["missions"]
        ),
        signals=CandidateSignals(
            commit_days=signals["commitDays"],
            missions_completed=signals["missionsCompleted"],
            missions_first_try=signals["missionsFirstTry"],
        ),
    )
