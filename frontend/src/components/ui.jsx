import React from "react";

export function Logo({ size = 36, withWordmark = true }) {
  return (
    <div
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "10px",
        userSelect: "none",
      }}
    >
      <span
        className="logo-mark"
        style={{
          position: "relative",
          width: size,
          height: size,
          borderRadius: "30%",
          background: "var(--grad-accent)",
          display: "inline-grid",
          placeItems: "center",
          fontFamily: "var(--font-display)",
          fontWeight: 700,
          color: "#04101f",
          fontSize: size * 0.42,
          boxShadow: "0 8px 24px rgba(47,116,255,0.35)",
        }}
        aria-hidden="true"
      >
        A
      </span>
      {withWordmark && (
        <span
          style={{
            fontFamily: "var(--font-display)",
            fontWeight: 600,
            fontSize: 18,
            letterSpacing: "0.01em",
            color: "var(--text-primary)",
          }}
        >
          AB<span style={{ color: "var(--accent)" }}>Talks</span>
        </span>
      )}
    </div>
  );
}

export function GlassCard({ children, className = "", style, as: Tag = "div", ...rest }) {
  return (
    <Tag
      className={`glass-card ${className}`}
      style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-lg)",
        backdropFilter: "blur(14px)",
        WebkitBackdropFilter: "blur(14px)",
        boxShadow: "var(--shadow-soft)",
        ...style,
      }}
      {...rest}
    >
      {children}
    </Tag>
  );
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  icon,
  style,
  ...rest
}) {
  const base = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
    border: "none",
    borderRadius: 999,
    fontFamily: "var(--font-display)",
    fontWeight: 600,
    cursor: disabled || loading ? "not-allowed" : "pointer",
    transition:
      "transform .18s ease, box-shadow .18s ease, background .18s ease, opacity .18s ease",
    whiteSpace: "nowrap",
    opacity: disabled || loading ? 0.6 : 1,
    position: "relative",
  };

  const sizes = {
    sm: { padding: "8px 14px", fontSize: 13 },
    md: { padding: "12px 20px", fontSize: 14 },
    lg: { padding: "16px 28px", fontSize: 16 },
  };

  const variants = {
    primary: {
      background: "var(--grad-accent)",
      color: "#04101f",
      boxShadow: "0 10px 30px rgba(47,116,255,0.30)",
    },
    ghost: {
      background: "var(--surface-strong)",
      color: "var(--text-primary)",
      border: "1px solid var(--border-strong)",
    },
    subtle: {
      background: "transparent",
      color: "var(--text-secondary)",
      border: "1px solid var(--border)",
    },
  };

  return (
    <button
      style={{ ...base, ...sizes[size], ...variants[variant], ...style }}
      disabled={disabled || loading}
      onMouseDown={(e) => {
        if (disabled || loading) return;
        e.currentTarget.style.transform = "scale(0.97)";
      }}
      onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
      onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
      {...rest}
    >
      {loading ? <Spinner size={16} /> : icon}
      <span>{children}</span>
    </button>
  );
}

export function Spinner({ size = 18 }) {
  return (
    <span
      style={{
        display: "inline-block",
        width: size,
        height: size,
        borderRadius: "50%",
        border: "2px solid rgba(4,16,31,0.25)",
        borderTopColor: "#04101f",
        animation: "spin 0.7s linear infinite",
      }}
      aria-label="Loading"
    />
  );
}

export function LightSpinner({ size = 18 }) {
  return (
    <span
      style={{
        display: "inline-block",
        width: size,
        height: size,
        borderRadius: "50%",
        border: "2px solid rgba(255,255,255,0.18)",
        borderTopColor: "var(--accent)",
        animation: "spin 0.7s linear infinite",
      }}
      aria-label="Loading"
    />
  );
}

export function Tag({ children, color = "primary", style }) {
  const colors = {
    primary: { bg: "rgba(47,116,255,0.14)", fg: "var(--primary)", border: "rgba(47,116,255,0.25)" },
    accent: { bg: "rgba(52,226,197,0.12)", fg: "var(--accent)", border: "rgba(52,226,197,0.25)" },
    success: { bg: "rgba(43,212,122,0.12)", fg: "var(--success)", border: "rgba(43,212,122,0.25)" },
    warning: { bg: "rgba(245,177,61,0.12)", fg: "var(--warning)", border: "rgba(245,177,61,0.25)" },
    neutral: { bg: "var(--surface-strong)", fg: "var(--text-secondary)", border: "var(--border)" },
  };
  const c = colors[color] || colors.primary;
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 6,
        padding: "5px 12px",
        borderRadius: 999,
        fontSize: 12,
        fontWeight: 500,
        letterSpacing: "0.01em",
        background: c.bg,
        color: c.fg,
        border: `1px solid ${c.border}`,
        ...style,
      }}
    >
      {children}
    </span>
  );
}

// inline keyframe for spinners (kept local to avoid polluting global CSS)
const styleTag = document.createElement("style");
styleTag.textContent = `@keyframes spin { to { transform: rotate(360deg); } }`;
if (typeof document !== "undefined" && !document.getElementById("__spin_kf")) {
  styleTag.id = "__spin_kf";
  document.head.appendChild(styleTag);
}
