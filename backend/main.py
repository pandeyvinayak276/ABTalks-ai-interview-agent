"""HTTP API skeleton for the ABTalks AI Interview Agent."""

from __future__ import annotations

from dataclasses import dataclass, field

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    """Start an interview with candidate, or continue it with message."""

    model_config = ConfigDict(extra="forbid")

    sessionId: str = Field(min_length=1)
    candidate: Candidate | None = None
    message: str | None = None

    @model_validator(mode="after")
    def validate_interview_turn(self) -> "InterviewRequest":
        if self.candidate is None and self.message is None:
            raise ValueError("Provide candidate to start an interview or message to continue one.")
        if self.candidate is not None and self.message is not None:
            raise ValueError("Provide either candidate or message, not both.")
        if self.message is not None and not self.message.strip():
            raise ValueError("message must not be blank.")
        return self


class Feedback(BaseModel):
    """Required feedback shape for a future completed interview response."""

    summary: str
    strengths: list[str]
    gaps: list[str]
    next: list[str]


class InterviewResponse(BaseModel):
    reply: str
    done: bool
    feedback: Feedback | None = None


@dataclass
class InterviewSession:
    candidate: Candidate
    messages: list[str] = field(default_factory=list)


app = FastAPI(title="ABTalks AI Interview Agent")
sessions: dict[str, InterviewSession] = {}


@app.post(
    "/api/interview",
    response_model=InterviewResponse,
    response_model_exclude_none=True,
)
def interview(request: InterviewRequest) -> InterviewResponse:
    """Initialize or continue a session identified by the supplied sessionId."""

    if request.candidate is not None:
        if request.sessionId in sessions:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An interview session already exists for this sessionId.",
            )

        sessions[request.sessionId] = InterviewSession(candidate=request.candidate)
        return InterviewResponse(reply="Welcome. Let's begin your interview.", done=False)

    session = sessions.get(request.sessionId)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No interview session exists for this sessionId. Start with a candidate payload.",
        )

    session.messages.append(request.message.strip())
    return InterviewResponse(reply="Interview in progress.", done=False)


@app.get("/health")
def health() -> dict[str, str]:
    """Minimal local readiness check."""

    return {"status": "ok"}
