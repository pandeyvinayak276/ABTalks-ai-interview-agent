# AI Usage Log

## Entry 01 — Project Planning

**Date:** 2026-08-08

**AI Tool:** ChatGPT

**Purpose:**  
Understand the ABTalks AI Interview Agent hackathon requirements,
submission rules, authenticity requirements, and plan the initial
architecture.

**Key decisions:**
- Build an adaptive conversational technical interviewer.
- Use the candidate's cohort learning history for personalization.
- Maintain interview state using `sessionId`.
- Support adaptive follow-up questions.
- Cover at least 8 questions across at least 4 curriculum days.
- Generate structured feedback at the end of the interview.
- Implement the required HTTP API contract.

**Outcome:**  
Established the initial development plan and project structure.

## Entry 02 — Repository Inspection

**Date:** 2026-08-08

**AI Tool:** Codex

**Prompt:**
> You are helping me develop the ABTalks AI Interview Agent hackathon project.

First, inspect the current repository.

Do NOT create or modify any files yet.

Tell me:
1. What files currently exist.
2. Whether the Git repository is correctly detected.
3. What you understand about the current project state.
4. What you recommend as the first backend implementation step.

Do not implement anything yet.

**Outcome:**
Codex inspected the repository, confirmed that Git was correctly
configured, and recommended starting with a minimal FastAPI service
after reviewing the official API specification.

**Human Decision:**
Reviewed the recommendation. No code was implemented yet.
