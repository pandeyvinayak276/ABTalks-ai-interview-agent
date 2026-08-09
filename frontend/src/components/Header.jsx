import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Logo, Button } from "./ui.jsx";

export default function Header({ showStart = true }) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <header
      style={{
        position: "relative",
        zIndex: 10,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "20px clamp(20px, 5vw, 48px)",
      }}
    >
      <Link to="/" style={{ display: "inline-flex" }}>
        <Logo />
      </Link>

      <nav style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <span
          className="hide-on-mobile"
          style={{
            color: "var(--text-muted)",
            fontSize: 13,
            fontFamily: "var(--font-display)",
          }}
        >
          Adaptive AI Interview Agent
        </span>
        {showStart && location.pathname !== "/setup" && (
          <Button
            size="sm"
            variant="ghost"
            onClick={() => navigate("/setup")}
          >
            Start Interview
          </Button>
        )}
      </nav>
    </header>
  );
}
