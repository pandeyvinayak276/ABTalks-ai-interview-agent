import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header.jsx";
import { GlassCard, Button, Tag } from "../components/ui.jsx";
import { useCandidate } from "../state/candidate.jsx";

export default function Results() {
  const navigate = useNavigate();
  const { session, clear } = useCandidate();

  React.useEffect(() => {
    if (!session || !session.done) {
      navigate("/setup", { replace: true });
    }
  }, [session, navigate]);

  if (!session || !session.done) return null;

  const fb = session.feedback || {};
  const summary = fb.summary || session.reply || "Interview complete.";
  const strengths = Array.isArray(fb.strengths) ? fb.strengths : [];
  const gaps = Array.isArray(fb.gaps) ? fb.gaps : [];
  const next = Array.isArray(fb.next) ? fb.next : [];
  const candidateName = session.candidate?.member?.name || "Candidate";
  const role = session.candidate?.member?.jobRole || "the role";

  const counts = [
    { label: "Strengths", value: strengths.length, color: "var(--success)" },
    { label: "Gaps", value: gaps.length, color: "var(--warning)" },
    { label: "Next steps", value: next.length, color: "var(--primary)" },
  ];

  function startNew() {
    clear();
    navigate("/setup", { replace: true });
  }

  return (
    <>
      <Header showStart={false} />
      <section
        style={{
          maxWidth: 980,
          margin: "0 auto",
          padding: "clamp(24px, 5vw, 48px) clamp(20px, 5vw, 48px) 64px",
        }}
      >
        {/* Hero */}
        <div style={{ textAlign: "center", animation: "fadeUp .5s ease both" }}>
          <div
            style={{
              width: 64,
              height: 64,
              borderRadius: "50%",
              margin: "0 auto 18px",
              display: "grid",
              placeItems: "center",
              background: "var(--grad-accent)",
              color: "#04101f",
              animation: "pulseRing 2.2s ease-out infinite, fadeUp .5s ease both",
            }}
          >
            <CheckIcon />
          </div>
          <Tag color="success" style={{ marginBottom: 16 }}>
            Interview Complete
          </Tag>
          <h1 style={{ fontSize: "clamp(28px, 4.5vw, 44px)", marginBottom: 10 }}>
            Nice work, {candidateName.split(" ")[0]}.
          </h1>
          <p style={{ color: "var(--text-secondary)", maxWidth: 520, margin: "0 auto", fontSize: 16 }}>
            Here's your adaptive evaluation for the <strong style={{ color: "var(--text-primary)" }}>{role}</strong> interview.
          </p>
        </div>

        {/* Stat row */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
            gap: 14,
            marginTop: 32,
            animation: "fadeUp .5s ease .05s both",
          }}
        >
          {counts.map((c) => (
            <GlassCard key={c.label} style={{ padding: "20px 22px", textAlign: "center" }}>
              <div
                style={{
                  fontFamily: "var(--font-display)",
                  fontWeight: 700,
                  fontSize: 34,
                  color: c.color,
                  lineHeight: 1,
                }}
              >
                {c.value}
              </div>
              <div style={{ color: "var(--text-muted)", fontSize: 13, marginTop: 6 }}>
                {c.label}
              </div>
            </GlassCard>
          ))}
        </div>

        {/* Summary */}
        <GlassCard
          style={{
            marginTop: 20,
            padding: "clamp(24px, 4vw, 32px)",
            animation: "fadeUp .5s ease .1s both",
            background: "var(--grad-accent-soft)",
            border: "1px solid var(--border-strong)",
          }}
        >
          <SectionHeading icon={<DocIcon />} title="Assessment summary" />
          <p style={{ color: "var(--text-primary)", fontSize: 16, lineHeight: 1.7, marginTop: 14 }}>
            {summary}
          </p>
        </GlassCard>

        {/* Strengths + Gaps */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            gap: 18,
            marginTop: 18,
          }}
        >
          <FeedbackColumn
            title="Strengths"
            icon={<UpIcon />}
            color="var(--success)"
            items={strengths}
            emptyText="No specific strengths flagged."
            delay=".15s"
          />
          <FeedbackColumn
            title="Gaps to address"
            icon={<DownIcon />}
            color="var(--warning)"
            items={gaps}
            emptyText="No significant gaps flagged."
            delay=".2s"
          />
        </div>

        {/* Next steps */}
        <GlassCard
          style={{
            marginTop: 18,
            padding: "clamp(24px, 4vw, 32px)",
            animation: "fadeUp .5s ease .25s both",
          }}
        >
          <SectionHeading icon={<CompassIcon />} title="Recommended next steps" />
          {next.length > 0 ? (
            <ol style={{ margin: "14px 0 0", padding: 0, listStyle: "none", counterReset: "step" }}>
              {next.map((n, i) => (
                <li
                  key={i}
                  style={{
                    counterIncrement: "step",
                    display: "flex",
                    gap: 14,
                    padding: "10px 0",
                    borderTop: i === 0 ? "none" : "1px solid var(--border)",
                    fontSize: 15,
                    color: "var(--text-secondary)",
                    lineHeight: 1.6,
                  }}
                >
                  <span
                    style={{
                      flexShrink: 0,
                      width: 26,
                      height: 26,
                      borderRadius: 8,
                      display: "grid",
                      placeItems: "center",
                      fontFamily: "var(--font-display)",
                      fontWeight: 600,
                      fontSize: 13,
                      background: "var(--surface-strong)",
                      border: "1px solid var(--border)",
                      color: "var(--accent)",
                    }}
                  >
                    {i + 1}
                  </span>
                  <span style={{ color: "var(--text-primary)" }}>{n}</span>
                </li>
              ))}
            </ol>
          ) : (
            <p style={{ color: "var(--text-muted)", marginTop: 14 }}>
              No specific next steps were provided.
            </p>
          )}
        </GlassCard>

        {/* CTA */}
        <div
          style={{
            marginTop: 32,
            display: "flex",
            gap: 12,
            justifyContent: "center",
            flexWrap: "wrap",
            animation: "fadeUp .5s ease .3s both",
          }}
        >
          <Button size="lg" variant="primary" icon={<ArrowIcon />} onClick={startNew}>
            Start New Interview
          </Button>
          <Button size="lg" variant="ghost" onClick={() => navigate("/")}>
            Back to home
          </Button>
        </div>
      </section>
    </>
  );
}

function FeedbackColumn({ title, icon, color, items, emptyText, delay }) {
  return (
    <GlassCard
      style={{
        padding: "clamp(22px, 3vw, 28px)",
        animation: `fadeUp .5s ease ${delay} both`,
      }}
    >
      <SectionHeading icon={icon} title={title} color={color} />
      {items.length > 0 ? (
        <ul style={{ margin: "14px 0 0", padding: 0, listStyle: "none", display: "flex", flexDirection: "column", gap: 10 }}>
          {items.map((s, i) => (
            <li
              key={i}
              style={{
                display: "flex",
                gap: 12,
                padding: "12px 14px",
                borderRadius: "var(--radius)",
                background: "var(--surface)",
                border: "1px solid var(--border)",
                fontSize: 14.5,
                color: "var(--text-secondary)",
                lineHeight: 1.55,
                animation: `fadeUp .4s ease ${0.05 * i}s both`,
              }}
            >
              <span
                style={{
                  flexShrink: 0,
                  marginTop: 2,
                  width: 8,
                  height: 8,
                  borderRadius: "50%",
                  background: color,
                  opacity: 0.9,
                }}
              />
              <span style={{ color: "var(--text-primary)" }}>{s}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p style={{ color: "var(--text-muted)", marginTop: 14 }}>{emptyText}</p>
      )}
    </GlassCard>
  );
}

function SectionHeading({ icon, title, color = "var(--text-primary)" }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <span
        style={{
          width: 34,
          height: 34,
          borderRadius: 10,
          display: "grid",
          placeItems: "center",
          background: "var(--surface-strong)",
          border: "1px solid var(--border)",
          color,
        }}
      >
        {icon}
      </span>
      <h3 style={{ fontSize: 18, color }}>{title}</h3>
    </div>
  );
}

function CheckIcon() {
  return (
    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M6 12.5l4 4 8-9" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function DocIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M7 3h7l4 4v14H7zM14 3v4h4" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function UpIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 19V6M7 11l5-5 5 5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function DownIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 5v13M7 13l5 5 5-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function CompassIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.7" />
      <path d="M15.5 8.5l-2 5-5 2 2-5 5-2Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
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
