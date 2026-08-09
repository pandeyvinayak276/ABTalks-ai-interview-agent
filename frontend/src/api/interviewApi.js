// API client for the existing FastAPI backend.
// Base URL is configurable via VITE_API_BASE_URL (defaults to http://localhost:8000).

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") || "http://localhost:8000";

export const FEEDBACK_SHAPE = null; // sentinel for docs; not used at runtime

export function generateSessionId() {
  // Short unique id suitable for a hackathon demo session.
  const rnd = Math.random().toString(36).slice(2, 10);
  const time = Date.now().toString(36);
  return `abtalks-${time}-${rnd}`;
}

async function parseJson(res) {
  const text = await res.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { raw: text };
    }
  }
  return { ok: res.ok, status: res.status, data };
}

export async function checkHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health`, {
      headers: { Accept: "application/json" },
    });
    const parsed = await parseJson(res);
    return parsed.ok;
  } catch {
    return false;
  }
}

export async function startInterview(payload) {
  // payload: { sessionId, candidate: {...} }
  const res = await fetch(`${BASE_URL}/api/interview`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(payload),
  });
  const parsed = await parseJson(res);
  if (!parsed.ok) {
    throw new Error(
      `Failed to start interview (HTTP ${parsed.status}). ${
        parsed.data?.detail || "Please make sure the backend is running."
      }`
    );
  }
  return parsed.data; // { reply, done, feedback? }
}

export async function continueInterview({ sessionId, message }) {
  const res = await fetch(`${BASE_URL}/api/interview`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ sessionId, message }),
  });
  const parsed = await parseJson(res);
  if (!parsed.ok) {
    throw new Error(
      `Interview request failed (HTTP ${parsed.status}). ${
        parsed.data?.detail || "Please try again."
      }`
    );
  }
  return parsed.data; // { reply, done, feedback? }
}
