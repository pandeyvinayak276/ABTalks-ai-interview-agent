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

## Entry 05 — Deterministic MVP Interview Planner

### AI Tool
Codex

### Prompt
Implement the next MVP component: a deterministic interview planner for
the ABTalks AI Interview Agent.

First inspect:
- backend/data_loader.py
- data/curriculum.json
- data/candidates.json
- backend/main.py

The planner must personalize an interview using the candidate's actual
mission history and the curriculum.

Create:
- backend/interview_planner.py

Requirements:

1. Define an interview state that tracks:
   - candidate/member ID
   - asked questions
   - curriculum days already covered
   - current question number
   - maximum/minimum question count
   - whether the interview is complete

2. The planner must guarantee:
   - minimum 8 questions
   - coverage of at least 4 different curriculum days
   - questions are grounded in curriculum content
   - no accidental duplicate questions
   - the interview can be advanced turn-by-turn

3. Personalization:
   - Prefer curriculum days associated with missions the candidate
     completed.
   - Use mission attempts as a difficulty signal.
   - If a candidate needed multiple attempts, allow the planner to mark
     that topic as a deeper-probe opportunity.
   - Do not invent candidate information.

4. Question planning:
   Implement deterministic planning for the initial/core questions.
   Each planned question should contain:
   - question number
   - curriculum day
   - curriculum topic/title
   - objective
   - difficulty
   - reason for selection
   - whether it is a follow-up

5. Follow-ups:
   The planner must support adding a follow-up question based on the
   previous answer/context, but it should NOT generate natural-language
   questions using an LLM yet.

   For now, return a structured follow-up instruction/context that a
   future LLM layer can use.

6. Completion:
   The planner must report done=true only after at least 8 questions have
   been completed AND at least 4 curriculum days have been covered.

7. Keep this component independent:
   - Do NOT add an LLM.
   - Do NOT add a vector database.
   - Do NOT implement final feedback yet.
   - Do NOT modify the supplied JSON files.
   - Do NOT rewrite the existing API unless required for a minimal import.
   - Keep the planner easy to test.

8. Add a small test/validation script or test function proving:
   - an interview can be initialized for a real candidate from the
     supplied data
   - at least 8 questions can be planned
   - at least 4 different curriculum days are covered
   - completion is false before the requirements are met and true after
     they are met

Run the validation and report:
- files created/modified
- test results
- any assumptions

Do NOT commit or push anything.

### Implementation Outcome
Codex created:
- `backend/interview_planner.py`
- `tests/test_interview_planner.py`

The planner now tracks:
- candidate/member ID
- questions asked and completed
- curriculum days covered
- current question number
- minimum and maximum question counts
- interview completion state

The planner prioritizes curriculum days associated with the candidate's
completed missions and uses mission attempts as a difficulty signal.

Missions with 3 or more attempts are marked as `deeper_probe`
opportunities.

The planner supports structured follow-up instructions while leaving
natural-language question generation to the future LLM layer.

### Validation
- 3 tests passed
- Real supplied candidate data was used (`CAND-001`)
- 8 questions were planned
- 8 distinct curriculum days were covered
- Interview remained incomplete before the eighth completion
- Interview became complete after the required conditions were met
- Structured follow-up behavior was verified

### Files Created
- `backend/interview_planner.py`
- `tests/test_interview_planner.py`

### Notes
No supplied data files were modified.
The FastAPI API was not modified.
No LLM, vector database, or final feedback system was implemented in
this step.

## Entry 06 — Adaptive Interview and Candidate-Specific Evaluation

### AI Tool

ChatGPT

### Purpose

Used ChatGPT to extend the deterministic interview planner into an
adaptive interview system capable of adjusting interview length based
on candidate performance and generating structured, candidate-specific
feedback.

### Interaction

ChatGPT helped design and implement:

- adaptive interview length while maintaining a minimum of 8 questions
- the ability to continue interviews beyond 8 questions for candidates
  demonstrating strong technical performance
- answer-quality classification into strong, good, adequate, and brief
- detection of concrete examples in candidate answers
- detection of technical reasoning
- detection of engineering trade-offs
- identification of strong and weaker curriculum topics
- personalized final feedback and recommended next steps
- candidate-specific follow-up and deeper-probing behavior
- preservation of the deterministic planner as the source of question
  selection
- integration of Breeth as a memory/context layer rather than a
  question generator

### Outcome

The interview agent successfully became adaptive instead of ending at a
fixed number of questions.

Testing with the supplied CAND-001 candidate demonstrated that a strong
candidate could progress to 13 questions while covering 8 curriculum
days.

The final evaluation successfully identified:

- 10 strong answers
- 3 good answers
- concrete examples
- technical reasoning
- engineering trade-off awareness
- no major curriculum weakness

The feedback system was also separately validated using a temporary
testing endpoint before the endpoint was removed from the final API.

### Implementation Impact

The resulting architecture now separates:

1. Candidate and curriculum data loading
2. Deterministic curriculum-grounded question planning
3. Adaptive interview progression
4. Candidate answer analysis
5. Structured follow-up and deeper probing
6. Candidate-specific final feedback
7. Breeth-based interview memory storage

The existing FastAPI interview API and supplied data files were
preserved.

## Entry 07 — Breeth Memory Integration and Adaptive Interview Context

### AI Tool

ChatGPT

### Purpose

Used ChatGPT to integrate Breeth memory into the adaptive interview
agent while keeping deterministic interview planning and candidate-facing
question generation separate from memory retrieval.

### Interaction

ChatGPT helped implement and validate:

- Breeth memory integration through `backend/breeth_memory.py`
- retrieval of relevant interview memories using the candidate's latest answer
- internal memory context that is not exposed directly to the candidate
- integration of Breeth retrieval into the existing adaptive interview flow
- preservation of deterministic curriculum-based question planning
- adaptive interview progression and structured answer analysis
- candidate-specific interview feedback

### Outcome

The interview agent can now retrieve relevant Breeth memories during an
active interview and use them as internal context without directly exposing
the retrieved memory to the candidate.

The deterministic planner remains responsible for selecting curriculum
topics and advancing the interview, while Breeth acts as a supporting
memory layer.

### Implementation Impact

The implementation now separates:

1. Candidate and curriculum data loading
2. Deterministic interview planning
3. Adaptive interview progression
4. Breeth-based memory retrieval
5. Candidate answer analysis
6. Structured interview feedback

Breeth retrieval is performed using the current curriculum context and,
when available, the candidate's latest answer.

Retrieved memory is kept internal and is not directly included in the
candidate-facing API response.

### Validation

- Real supplied candidate data was used (`CAND-001`)
- A new interview session was successfully initialized
- The first curriculum-grounded question was generated successfully
- A candidate answer was successfully processed
- Breeth memory retrieval did not interrupt the interview flow
- The next interview question was generated successfully
- Retrieved memory was not leaked into the candidate-facing response
- No `422` or `500` error occurred during the validation
- The adaptive interview remained active after the tested turn

