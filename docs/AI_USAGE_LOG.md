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
 You are helping me develop the ABTalks AI Interview Agent hackathon project.

First, inspect the current repository.

Do NOT create or modify any files yet.

Tell me:
1. What files currenty exist.
2. Whether the Git reository is correctly detected.
3. What you understand about the current project state.
4. What you recommend as the first backend implementation step.

Do not implement anything yet.

**Outcome:**
Codex inspected the repository, confirmed that Git was correctly
configured, and recommended starting with a minimal FastAPI service
after reviewing the official API specification.

**Human Decision:**
Reviewed the recommendation. No code was implemented yet.

## Entry 03 — Initial FastAPI API Skeleton

### AI Tool
Codex

### Prompt
Now implement ONLY the initial API skeleton for the ABTalks AI Interview Agent.

First, inspect the official Technical Specification in the data/ directory and use it as the source of truth for the API contract.

Implement only:
- FastAPI application setup
- Required POST /api/interview endpoint
- Request and response models
- Basic session handling using sessionId
- Basic request validation
- Minimal health endpoint for local testing

Do not implement LLM integration, adaptive questioning, curriculum retrieval, candidate personalization, answer evaluation, feedback generation, vector database, RAG, or authentication.

Do not modify data/ or AI_USAGE_LOG.md.
Do not commit or push anything.

### Outcome
Codex created the initial FastAPI API skeleton with:
- POST /api/interview
- GET /health
- Typed request/response models
- In-memory session handling
- Basic validation
- FastAPI and Uvicorn dependencies

The API was tested locally through Swagger UI. The health endpoint returned HTTP 200, the interview session initialized successfully, and a second request using the same sessionId returned HTTP 200.

### Validation
- FastAPI server started successfully.
- GET /health returned 200 OK.
- POST /api/interview returned 200 OK for session initialization.
- Continuing the same sessionId returned 200 OK.