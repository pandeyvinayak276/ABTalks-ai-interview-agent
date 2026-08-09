# ABTalks — Frontend

Premium React UI for the **ABTalks Adaptive AI Interview Agent**. This is a
frontend-only client that talks to your existing FastAPI backend.

## Run locally

```bash
cd frontend
npm install
npm run dev
```

The app starts on http://localhost:5173.

## Configure the backend URL

The API base URL is configurable via an environment variable. It defaults to
`http://localhost:8000`. To point at a different backend, edit `frontend/.env`:

```
VITE_API_BASE_URL=http://localhost:8000
```

Restart `npm run dev` after changing it.

## Backend API contract used

The frontend calls a single endpoint:

`POST /api/interview`

- **Start** — body: `{ sessionId, candidate: { member: { id, name, jobRole, yearsExperience, education, status }, missions: [], signals: { commitDays, missionsCompleted, missionsFirstTry } } }`
  → `{ reply, done }`
- **Continue** — body: `{ sessionId, message }`
  → `{ reply, done }` or, when complete, `{ reply, done: true, feedback: { summary, strengths[], gaps[], next[] } }`

A `GET /health` check is also supported (used for connectivity, optional).

> The frontend makes no assumptions about backend logic — it only sends the
> payload above and renders the backend's replies verbatim.

## Project structure

```
frontend/
  src/
    api/interviewApi.js      # fetch client for the FastAPI backend
    components/              # Header, AuroraBackground, shared UI primitives
    pages/                   # Landing, Setup, Interview, Results
    state/candidate.jsx      # in-memory + sessionStorage session store
    App.jsx, main.jsx        # routing + providers
  .env                      # VITE_API_BASE_URL
```
