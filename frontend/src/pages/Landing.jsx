import React from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header.jsx";
import { GlassCard, Button, Tag } from "../components/ui.jsx";

const FEATURES = [
  {
    icon: AdaptIcon,
    title: "Adaptive",
    desc: "Questions evolve in real time based on your answers, drilling into depth and surfacing the signals that matter.",
    color: "var(--primary)",
  },
  {
    icon: EvalIcon,
    title: "AI Evaluated",
    desc: "Every response is assessed instantly for clarity, reasoning, and technical accuracy — no waiting for a panel.",
    color: "var(--accent)",
  },
  {
    icon: PersonaIcon,
    title: "Personalized",
    desc: "The interview is tailored to your role, experience, and background for a fair, relevant conversation.",
    color: "var(--success)",
  },
];

const STEPS = [
  { n: "01", t: "Set your profile", d: "Role, experience, education — takes seconds." },
  { n: "02", t: "Talk with the agent", d: "Answer adaptive questions in a focused flow." },
  { n: "03", t: "Get instant feedback", d: "Strengths, gaps, and next steps in one report." },
];

export default function Landing() {
  const navigate = useNavigate();
  return (
    <>
      <Header showStart={false} />

      {/* Hero */}
      <section
        style={{
          maxWidth: 1180,
          margin: "0 auto",
          padding: "clamp(40px, 8vw, 96px) clamp(20px, 5vw, 48px) 0",
          textAlign: "center",
        }}
      >
        <div style={{ animation: "fadeUp .6s ease both" }}>
          <Tag color="accent" style={{ marginBottom: 24 }}>
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
            Adaptive AI Technical Interview Agent
          </Tag>
        </div>

        <h1
          style={{
            fontSize: "clamp(36px, 6.5vw, 76px)",
            fontWeight: 700,
            lineHeight: 1.05,
            maxWidth: 900,
            margin: "0 auto",
            animation: "fadeUp .6s ease .05s both",
          }}
        >
          Technical interviews that{" "}
          <span
            style={{
              background: "var(--grad-accent)",
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              color: "transparent",
            }}
          >
            adapt to you.
          </span>
        </h1>

        <p
          style={{
            fontSize: "clamp(16px, 2vw, 20px)",
            color: "var(--text-secondary)",
            maxWidth: 640,
            margin: "24px auto 0",
            animation: "fadeUp .6s ease .1s both",
          }}
        >
          ABTalks runs a live, conversational technical interview that adjusts
          to your answers in real time — then delivers an instant,
          structured evaluation.
        </p>

        <div
          style={{
            marginTop: 36,
            display: "flex",
            gap: 14,
            justifyContent: "center",
            flexWrap: "wrap",
            animation: "fadeUp .6s ease .15s both",
          }}
        >
          <Button
            size="lg"
            variant="primary"
            icon={<ArrowIcon />}
            onClick={() => navigate("/setup")}
          >
            Start Interview
          </Button>
          <Button size="lg" variant="ghost" onClick={() => navigate("/setup")}>
            Try the demo
          </Button>
        </div>

        <p
          style={{
            marginTop: 18,
            color: "var(--text-muted)",
            fontSize: 13,
            animation: "fadeIn .8s ease .4s both",
          }}
        >
          No signup. Pre-filled demo profile so you can start in one click.
        </p>
      </section>

      {/* Product preview mock */}
      <section
        style={{
          maxWidth: 980,
          margin: "56px auto 0",
          padding: "0 clamp(20px, 5vw, 48px)",
          animation: "fadeUp .7s ease .25s both",
        }}
      >
        <GlassCard
          style={{
            padding: 0,
            overflow: "hidden",
            border: "1px solid var(--border-strong)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              padding: "14px 18px",
              borderBottom: "1px solid var(--border)",
              background: "rgba(255,255,255,0.02)",
            }}
          >
            <Dot color="#ff5a6e" />
            <Dot color="#f5b13d" />
            <Dot color="#2bd47a" />
            <span
              style={{
                marginLeft: 10,
                fontSize: 12,
                color: "var(--text-muted)",
                fontFamily: "var(--font-display)",
              }}
            >
              abtalks · interview session
            </span>
          </div>
          <div
            style={{
              padding: "clamp(24px, 4vw, 40px)",
              display: "grid",
              gridTemplateColumns: "minmax(0,1fr)",
              gap: 20,
              textAlign: "left",
            }}
          >
            <ChatBubble role="ai">
              Let's start with systems design. Walk me through how you'd design
              a rate limiter that scales across regions.
            </ChatBubble>
            <ChatBubble role="user">
              I'd begin by clarifying constraints, then pick a token-bucket
              approach backed by Redis with regional coordination…
            </ChatBubble>
            <ChatBubble role="ai" typing />
          </div>
        </GlassCard>
      </section>

      {/* Features */}
      <section
        style={{
          maxWidth: 1180,
          margin: "0 auto",
          padding: "clamp(80px, 10vw, 120px) clamp(20px, 5vw, 48px) 0",
        }}
      >
        <SectionLabel>What makes it different</SectionLabel>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
            gap: 20,
            marginTop: 28,
          }}
        >
          {FEATURES.map((f, i) => (
            <GlassCard
              key={f.title}
              style={{
                padding: 28,
                animation: `fadeUp .6s ease ${0.05 * i}s both`,
                transition: "transform .25s ease, border-color .25s ease",
              }}
            >
              <div
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-4px)";
                  e.currentTarget.style.borderColor = "var(--border-strong)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.borderColor = "var(--border)";
                }}
                style={{
                  height: "100%",
                  transition: "transform .25s ease, border-color .25s ease",
                }}
              >
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 12,
                    display: "grid",
                    placeItems: "center",
                    background: "var(--surface-strong)",
                    border: "1px solid var(--border)",
                    color: f.color,
                    marginBottom: 18,
                  }}
                >
                  <f.icon />
                </div>
                <h3 style={{ fontSize: 19, marginBottom: 8 }}>{f.title}</h3>
                <p style={{ color: "var(--text-secondary)", fontSize: 14.5 }}>
                  {f.desc}
                </p>
              </div>
            </GlassCard>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section
        style={{
          maxWidth: 1180,
          margin: "0 auto",
          padding: "clamp(40px, 6vw, 64px) clamp(20px, 5vw, 48px) 0",
        }}
      >
        <SectionLabel>How it works</SectionLabel>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
            gap: 16,
            marginTop: 28,
          }}
        >
          {STEPS.map((s) => (
            <div
              key={s.n}
              style={{
                padding: "24px 22px",
                borderRadius: "var(--radius-lg)",
                background: "var(--surface)",
                border: "1px solid var(--border)",
              }}
            >
              <div
                style={{
                  fontFamily: "var(--font-display)",
                  fontWeight: 700,
                  fontSize: 13,
                  color: "var(--accent)",
                  letterSpacing: "0.08em",
                }}
              >
                {s.n}
              </div>
              <h4 style={{ fontSize: 17, margin: "10px 0 6px" }}>{s.t}</h4>
              <p style={{ color: "var(--text-secondary)", fontSize: 14 }}>
                {s.d}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section
        style={{
          maxWidth: 1180,
          margin: "0 auto",
          padding: "clamp(64px, 10vw, 120px) clamp(20px, 5vw, 48px)",
        }}
      >
        <GlassCard
          style={{
            padding: "clamp(36px, 6vw, 64px)",
            textAlign: "center",
            background: "var(--grad-accent-soft)",
            border: "1px solid var(--border-strong)",
            animation: "fadeUp .6s ease both",
          }}
        >
          <h2 style={{ fontSize: "clamp(26px, 4vw, 40px)", marginBottom: 14 }}>
            Ready when you are.
          </h2>
          <p
            style={{
              color: "var(--text-secondary)",
              maxWidth: 520,
              margin: "0 auto 28px",
              fontSize: 16,
            }}
          >
            Start a focused, adaptive interview in under a minute. No account,
            no setup friction — just a real conversation.
          </p>
          <Button
            size="lg"
            variant="primary"
            icon={<ArrowIcon />}
            onClick={() => navigate("/setup")}
          >
            Start Interview
          </Button>
        </GlassCard>
      </section>

      <Footer />
    </>
  );
}

function SectionLabel({ children }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        color: "var(--text-muted)",
        fontFamily: "var(--font-display)",
        fontSize: 13,
        letterSpacing: "0.06em",
        textTransform: "uppercase",
      }}
    >
      <span
        style={{ width: 24, height: 1, background: "var(--border-strong)" }}
      />
      {children}
    </div>
  );
}

function ChatBubble({ role, children, typing }) {
  const isAi = role === "ai";
  return (
    <div
      style={{
        display: "flex",
        gap: 12,
        alignItems: "flex-start",
        animation: "fadeUp .4s ease both",
      }}
    >
      <Avatar ai={isAi} />
      <div
        style={{
          maxWidth: "80%",
          padding: "14px 18px",
          borderRadius: 16,
          background: isAi ? "var(--surface-strong)" : "var(--grad-accent)",
          color: isAi ? "var(--text-primary)" : "#04101f",
          border: isAi ? "1px solid var(--border)" : "none",
          fontWeight: isAi ? 400 : 500,
          fontSize: 14.5,
        }}
      >
        {typing ? <TypingDots /> : children}
      </div>
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

function Dot({ color }) {
  return (
    <span
      style={{ width: 10, height: 10, borderRadius: "50%", background: color, opacity: 0.85 }}
    />
  );
}

function Footer() {
  return (
    <footer
      style={{
        borderTop: "1px solid var(--border)",
        marginTop: 40,
        padding: "28px clamp(20px, 5vw, 48px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: 12,
        color: "var(--text-muted)",
        fontSize: 13,
      }}
    >
      <span>ABTalks · Adaptive AI Interview Agent</span>
      <span>
        Built for hackathon demo ·{" "}
        <a href="/download" style={{ color: "var(--accent)", textDecoration: "none" }}>
          Download frontend
        </a>
      </span>
    </footer>
  );
}

/* icons (inline, no deps) */
function ArrowIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function AdaptIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M4 7h10M4 12h6M4 17h13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      <path d="M18 14l3 3-3 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function EvalIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M9 11l2 2 4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}
function PersonaIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2" />
      <path d="M4 20c0-3.3 3.6-6 8-6s8 2.7 8 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
