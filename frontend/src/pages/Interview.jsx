import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header.jsx";
import { GlassCard, Button, Tag, LightSpinner } from "../components/ui.jsx";
import { useCandidate } from "../state/candidate.jsx";
import { continueInterview } from "../api/interviewApi.js";

export default function Interview() {
  const navigate = useNavigate();
  const { session, setSession, clear } = useCandidate();

  // Guard: if someone lands here without an active session, send them to setup.
  React.useEffect(() => {
    if (!session || !session.reply) {
      navigate("/setup", { replace: true });
    }
  }, [session, navigate]);

  const [answer, setAnswer] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const scrollRef = React.useRef(null);
  const textareaRef = React.useRef(null);

  // Auto-scroll to latest message.
  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [session?.history, loading]);

  // Keep focus on the textarea when a new question arrives.
  React.useEffect(() => {
    if (!loading && textareaRef.current) textareaRef.current.focus();
  }, [session?.reply, loading]);

  if (!session || !session.reply) return null;

  const currentQuestion = session.reply;
  const questionNumber = session.questionCount || 1;

  async function handleSubmit(e) {
    e?.preventDefault();
    const text = answer.trim();
    if (!text || loading) return;

    setLoading(true);
    setError(null);

    // Optimistically add the candidate's message to the transcript.
    const userMsg = { role: "user", text };
    setSession((prev) => ({
      ...prev,
      history: [...(prev.history || []), userMsg],
    }));
    setAnswer("");

    try {
      const res = await continueInterview({
        sessionId: session.sessionId,
        message: text,
      });

      const aiMsg = { role: "ai", text: res.reply ?? "" };

      if (res.done) {
        setSession((prev) => ({
          ...prev,
          reply: res.reply ?? "",
          done: true,
          feedback: res.feedback ?? null,
          history: [...(prev.history || []), aiMsg],
        }));
        // Small delay so the user sees the final reply before transitioning.
        setTimeout(() => navigate("/results"), 700);
        return;
      }

      setSession((prev) => ({
        ...prev,
        reply: res.reply ?? "",
        done: false,
        questionCount: (prev.questionCount || 1) + 1,
        history: [...(prev.history || []), aiMsg],
      }));
    } catch (err) {
      setError(err.message || "Something went wrong reaching the interview agent.");
      // Put the unsent answer back so the candidate can retry.
      setAnswer(text);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      handleSubmit(e);
    }
  }

  function handleAbort() {
    clear();
    navigate("/setup", { replace: true });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <Header showStart={false} />

      <div
        style={{
          flex: 1,
          maxWidth: 880,
          width: "100%",
          margin: "0 auto",
          padding: "8px clamp(20px, 5vw, 48px) 32px",
          display: "flex",
          flexDirection: "column",
          gap: 20,
        }}
      >
        {/* Session meta + progress */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 14,
            flexWrap: "wrap",
            animation: "fadeUp .4s ease both",
          }}
        >
          <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
            <Tag color="accent">
              <span
                style={{
                  width: 6,
                  height: 6,
                  borderRadius: "50%",
                  background: "var(--accent)",
                  display: "inline-block",
                  animation: "pulseRing 2s ease-out infinite",
                }}
              />
              Live interview
            </Tag>
            <Tag color="neutral">{session.candidate?.member?.name}</Tag>
            <Tag color="neutral">{session.candidate?.member?.jobRole}</Tag>
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              color: "var(--text-muted)",
              fontSize: 13,
              fontFamily: "var(--font-display)",
            }}
          >
            Question {questionNumber}
          </div>
        </div>

        <ProgressBar value={Math.min(questionNumber, 8)} max={8} />

        {/* Transcript */}
        <GlassCard
          style={{
            flex: 1,
            minHeight: "min(46vh, 360px)",
            padding: 0,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div
            ref={scrollRef}
            style={{
              padding: "clamp(18px, 3vw, 28px)",
              overflowY: "auto",
              display: "flex",
              flexDirection: "column",
              gap: 18,
              flex: 1,
            }}
          >
            {(session.history || []).map((m, i) => (
              <Message key={i} role={m.role} text={m.text} />
            ))}
            {loading && <Message role="ai" typing />}
          </div>
        </GlassCard>

        {/* Composer */}
        <GlassCard
          style={{
            padding: "clamp(16px, 3vw, 22px)",
            animation: "fadeUp .4s ease .05s both",
          }}
        >
          {/* Current question prompt (always visible above the textarea) */}
          <div
            style={{
              marginBottom: 14,
              padding: "14px 16px",
              borderRadius: "var(--radius)",
              background: "var(--grad-accent-soft)",
              border: "1px solid var(--border)",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                marginBottom: 8,
                color: "var(--accent)",
                fontFamily: "var(--font-display)",
                fontSize: 12,
                letterSpacing: "0.06em",
                textTransform: "uppercase",
              }}
            >
              <AiGlyph /> ABTalks · Question {questionNumber}
            </div>
            <p style={{ fontSize: 15.5, color: "var(--text-primary)", lineHeight: 1.6 }}>
              {currentQuestion}
            </p>
          </div>

          <form onSubmit={handleSubmit}>
            <div
              style={{
                position: "relative",
                borderRadius: "var(--radius)",
                border: "1px solid var(--border)",
                background: "rgba(255,255,255,0.03)",
                transition: "border-color .18s ease",
              }}
            >
              <textarea
                ref={textareaRef}
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your answer…  (⌘/Ctrl + Enter to submit)"
                disabled={loading}
                rows={5}
                style={{
                  width: "100%",
                  background: "transparent",
                  border: "none",
                  outline: "none",
                  color: "var(--text-primary)",
                  fontSize: 15,
                  lineHeight: 1.6,
                  padding: "14px 16px",
                  resize: "vertical",
                  minHeight: 130,
                }}
              />
            </div>

            {error && (
              <div
                role="alert"
                style={{
                  marginTop: 12,
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
                <span>{error}</span>
              </div>
            )}

            <div
              style={{
                marginTop: 14,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: 12,
                flexWrap: "wrap",
              }}
            >
              <span style={{ color: "var(--text-muted)", fontSize: 12.5 }}>
                {loading ? "ABTalks is thinking…" : `${answer.trim().split(/\s+/).filter(Boolean).length} words`}
              </span>
              <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                <Button
                  type="button"
                  variant="subtle"
                  size="md"
                  onClick={handleAbort}
                  disabled={loading}
                >
                  End session
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  loading={loading}
                  disabled={loading || !answer.trim()}
                  icon={!loading ? <SendIcon /> : undefined}
                >
                  {loading ? "Submitting…" : "Submit Answer"}
                </Button>
              </div>
            </div>
          </form>
        </GlassCard>
      </div>
    </div>
  );
}

function Message({ role, text, typing }) {
  const isAi = role === "ai";
  return (
    <div
      style={{
        display: "flex",
        gap: 12,
        alignItems: "flex-start",
        animation: "fadeUp .35s ease both",
        justifyContent: isAi ? "flex-start" : "flex-end",
      }}
    >
      {isAi && <Avatar ai />}
      <div
        style={{
          maxWidth: "82%",
          padding: "13px 17px",
          borderRadius: 16,
          background: isAi ? "var(--surface-strong)" : "var(--grad-accent)",
          color: isAi ? "var(--text-primary)" : "#04101f",
          border: isAi ? "1px solid var(--border)" : "none",
          fontWeight: isAi ? 400 : 500,
          fontSize: 14.5,
          lineHeight: 1.6,
        }}
      >
        {typing ? <TypingDots /> : <span style={{ whiteSpace: "pre-wrap" }}>{text}</span>}
      </div>
      {!isAi && <Avatar ai={false} />}
    </div>
  );
}

function Avatar({ ai }) {
  return (
    <div
      style={{
        width: 30,
        height: 30,
        borderRadius: 8,
        flexShrink: 0,
        display: "grid",
        placeItems: "center",
        fontFamily: "var(--font-display)",
        fontWeight: 700,
        fontSize: 12,
        background: ai ? "var(--grad-accent)" : "var(--surface-strong)",
        color: ai ? "#04101f" : "var(--text-secondary)",
        border: ai ? "none" : "1px solid var(--border)",
      }}
    >
      {ai ? "AI" : "You"}
    </div>
  );
}

function TypingDots() {
  return (
    <span style={{ display: "inline-flex", gap: 5, padding: "2px 0" }}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          style={{
            width: 7,
            height: 7,
            borderRadius: "50%",
            background: "var(--text-secondary)",
            animation: "dotPulse 1.2s ease-in-out infinite",
            animationDelay: `${i * 0.18}s`,
          }}
        />
      ))}
    </span>
  );
}

function ProgressBar({ value, max }) {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div
      style={{
        height: 6,
        borderRadius: 999,
        background: "var(--surface-strong)",
        overflow: "hidden",
        animation: "fadeUp .4s ease both",
      }}
    >
      <div
        style={{
          height: "100%",
          width: `${pct}%`,
          background: "var(--grad-accent)",
          borderRadius: 999,
          transition: "width .5s cubic-bezier(.2,.8,.2,1)",
        }}
      />
    </div>
  );
}

function AiGlyph() {
  return (
    <span
      style={{
        width: 8,
        height: 8,
        borderRadius: 2,
        background: "var(--accent)",
        display: "inline-block",
      }}
    />
  );
}
function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M5 12l14-7-5 14-3-6-6-1Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
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
