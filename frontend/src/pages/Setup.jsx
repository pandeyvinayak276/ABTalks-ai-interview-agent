import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header.jsx";
import { GlassCard, Button, Tag } from "../components/ui.jsx";
import { useCandidate } from "../state/candidate.jsx";
import { startInterview, generateSessionId } from "../api/interviewApi.js";

const DEFAULTS = {
  name: "Alex Morgan",
  memberId: "M-1042",
  jobRole: "Backend Engineer",
  yearsExperience: 4,
  education: "B.Sc. Computer Science",
  status: "Available",
};

export default function Setup() {
  const navigate = useNavigate();
  const { setSession } = useCandidate();

  const [form, setForm] = React.useState(DEFAULTS);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);

  const update = (k) => (e) =>
    setForm((f) => ({
      ...f,
      [k]: k === "yearsExperience" ? Number(e.target.value) : e.target.value,
    }));

  async function handleStart(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const sessionId = generateSessionId();
    const candidate = {
      member: {
        id: form.memberId.trim() || "demo-candidate",
        name: form.name.trim() || "Candidate",
        jobRole: form.jobRole.trim() || "Generalist",
        yearsExperience: Number(form.yearsExperience) || 0,
        education: form.education.trim() || "—",
        status: form.status.trim() || "Available",
      },
      missions: [],
      signals: {
        commitDays: 0,
        missionsCompleted: 0,
        missionsFirstTry: 0,
      },
    };

    try {
      const res = await startInterview({ sessionId, candidate });
      setSession({
        sessionId,
        candidate,
        reply: res.reply ?? "",
        done: Boolean(res.done),
        feedback: res.feedback ?? null,
        questionCount: 1,
        history: [{ role: "ai", text: res.reply ?? "" }],
      });
      navigate("/interview");
    } catch (err) {
      setError(err.message || "Could not reach the interview backend.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <Header />
      <section
        style={{
          maxWidth: 880,
          margin: "0 auto",
          padding: "clamp(24px, 5vw, 48px) clamp(20px, 5vw, 48px) 64px",
        }}
      >
        <div style={{ animation: "fadeUp .5s ease both" }}>
          <Tag color="primary" style={{ marginBottom: 18 }}>
            Step 1 of 3 · Candidate setup
          </Tag>
          <h1 style={{ fontSize: "clamp(28px, 4.5vw, 44px)", marginBottom: 10 }}>
            Tell ABTalks who you are
          </h1>
          <p style={{ color: "var(--text-secondary)", maxWidth: 560, fontSize: 16 }}>
            We use this to tailor the interview. Defaults are pre-filled so you
            can start the demo instantly.
          </p>
        </div>

        <GlassCard
          style={{
            marginTop: 28,
            padding: "clamp(24px, 4vw, 36px)",
            animation: "fadeUp .5s ease .08s both",
          }}
        >
          <form onSubmit={handleStart}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                gap: 18,
              }}
            >
              <Field label="Full name">
                <input
                  value={form.name}
                  onChange={update("name")}
                  placeholder="Alex Morgan"
                  style={inputStyle}
                  required
                />
              </Field>
              <Field label="Candidate / member ID">
                <input
                  value={form.memberId}
                  onChange={update("memberId")}
                  placeholder="M-1042"
                  style={inputStyle}
                  required
                />
              </Field>
              <Field label="Job role">
                <input
                  value={form.jobRole}
                  onChange={update("jobRole")}
                  placeholder="Backend Engineer"
                  style={inputStyle}
                  required
                />
              </Field>
              <Field label="Years of experience">
                <input
                  type="number"
                  min="0"
                  max="50"
                  value={form.yearsExperience}
                  onChange={update("yearsExperience")}
                  style={inputStyle}
                  required
                />
              </Field>
              <Field label="Education">
                <input
                  value={form.education}
                  onChange={update("education")}
                  placeholder="B.Sc. Computer Science"
                  style={inputStyle}
                  required
                />
              </Field>
              <Field label="Status">
                <select
                  value={form.status}
                  onChange={update("status")}
                  style={inputStyle}
                >
                  <option>Available</option>
                  <option>Open to offers</option>
                  <option>Employed</option>
                  <option>Exploring</option>
                  <option>Student</option>
                </select>
              </Field>
            </div>

            <div
              style={{
                marginTop: 16,
                display: "flex",
                alignItems: "center",
                gap: 10,
                color: "var(--text-muted)",
                fontSize: 13,
              }}
            >
              <InfoIcon />
              A unique session ID is generated automatically when you start.
            </div>

            {error && <ErrorBanner message={error} />}

            <div
              style={{
                marginTop: 26,
                display: "flex",
                gap: 12,
                flexWrap: "wrap",
                alignItems: "center",
              }}
            >
              <Button
                type="submit"
                size="lg"
                variant="primary"
                loading={loading}
                icon={!loading ? <ArrowIcon /> : undefined}
                disabled={loading}
              >
                {loading ? "Starting interview…" : "Start Interview"}
              </Button>
              <Button
                type="button"
                size="lg"
                variant="subtle"
                onClick={() => setForm(DEFAULTS)}
                disabled={loading}
              >
                Reset to demo defaults
              </Button>
            </div>
          </form>
        </GlassCard>
      </section>
    </>
  );
}

function Field({ label, children }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <span
        style={{
          fontSize: 13,
          color: "var(--text-secondary)",
          fontFamily: "var(--font-display)",
          fontWeight: 500,
        }}
      >
        {label}
      </span>
      {children}
    </label>
  );
}

const inputStyle = {
  width: "100%",
  padding: "12px 14px",
  borderRadius: "var(--radius)",
  background: "rgba(255,255,255,0.03)",
  border: "1px solid var(--border)",
  color: "var(--text-primary)",
  fontSize: 14.5,
  outline: "none",
  transition: "border-color .18s ease, box-shadow .18s ease",
};

function ErrorBanner({ message }) {
  return (
    <div
      role="alert"
      style={{
        marginTop: 18,
        display: "flex",
        gap: 10,
        alignItems: "flex-start",
        padding: "12px 14px",
        borderRadius: "var(--radius)",
        background: "rgba(255,90,110,0.10)",
        border: "1px solid rgba(255,90,110,0.30)",
        color: "#ffd0d6",
        fontSize: 14,
        animation: "fadeUp .3s ease both",
      }}
    >
      <WarnIcon />
      <span>{message}</span>
    </div>
  );
}

function InfoIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.6" />
      <path d="M12 11v5M12 7.5v.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}
function WarnIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true" style={{ flexShrink: 0, marginTop: 1 }}>
      <path d="M12 8v5M12 16v.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M10.3 4.5 2.6 18a2 2 0 0 0 1.7 3h15.4a2 2 0 0 0 1.7-3L13.7 4.5a2 2 0 0 0-3.4 0Z" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}
function ArrowIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
