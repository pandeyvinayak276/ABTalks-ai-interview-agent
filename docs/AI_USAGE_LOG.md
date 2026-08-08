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

## Entry 04 — Read-Only Curriculum and Candidate Data Loader

### AI Tool
Codex

### Prompt
Implement the next small feature: read-only loaders for the official
curriculum and candidate data.

First inspect:
- data/curriculum.json
- data/candidates.json

Use their ACTUAL schemas. Do not guess or invent fields.

Create a small data-loading module that:
1. Loads curriculum.json.
2. Loads candidates.json.
3. Provides typed Python structures/models for the data we will need later.
4. Allows the interview engine to retrieve:
   - a candidate by member ID
   - curriculum information by day
5. Keeps the original JSON files completely unchanged.

Important:
- Do NOT implement LLM integration.
- Do NOT implement question generation.
- Do NOT implement evaluation or feedback.
- Do NOT modify the FastAPI endpoint yet unless a minimal import change is
  absolutely necessary.
- Do NOT add a database or vector database.
- Do NOT modify docs/AI_USAGE_LOG.md.
- Keep the implementation simple and testable.

Before changing files, briefly explain the files you plan to create.

After implementation:
- Run a small validation/test proving that the loaders can read the
  supplied JSON files and retrieve a candidate and curriculum day.
- Report exactly which files were changed/created.
- Do NOT commit or push anything.

### Implementation Outcome
Codex inspected the supplied curriculum and candidate JSON files and created:

- `backend/data_loader.py`

The loader provides immutable typed structures for:

- Curriculum root, modules, and daily curriculum entries
- Candidates and member information
- Mission history
- Engagement signals

No changes were made to:
- `data/curriculum.json`
- `data/candidates.json`
- `docs/AI_USAGE_LOG.md`
- The existing FastAPI endpoint

### Validation
The implementation was successfully validated:

- PASS: loaded 20 candidates and 31 curriculum days
- PASS: candidate `CAND-001` = Sarah Johnson
- PASS: day 7 = Embeddings Explained
- PASS: `git diff --check`

### Files Changed
- `backend/data_loader.py` — created
- `docs/AI_USAGE_LOG.md` — manually updated with this entry