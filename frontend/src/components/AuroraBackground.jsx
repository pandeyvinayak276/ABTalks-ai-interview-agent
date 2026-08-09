import React from "react";

export default function AuroraBackground({ variant = "default" }) {
  return (
    <div
      aria-hidden="true"
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 0,
        overflow: "hidden",
        background: "var(--grad-hero)",
        pointerEvents: "none",
      }}
    >
      {/* Floating orbs */}
      <div
        style={{
          position: "absolute",
          top: "-12%",
          right: "-6%",
          width: 520,
          height: 520,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(47,116,255,0.22), transparent 65%)",
          filter: "blur(20px)",
          animation: "floatGlow 12s ease-in-out infinite",
        }}
      />
      <div
        style={{
          position: "absolute",
          bottom: "-14%",
          left: "-8%",
          width: 480,
          height: 480,
          borderRadius: "50%",
          background:
            "radial-gradient(circle, rgba(52,226,197,0.16), transparent 65%)",
          filter: "blur(24px)",
          animation: "floatGlow 15s ease-in-out infinite",
          animationDelay: "-3s",
        }}
      />

      {/* Subtle grid */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
          maskImage:
            "radial-gradient(ellipse 80% 60% at 50% 30%, #000 30%, transparent 90%)",
          WebkitMaskImage:
            "radial-gradient(ellipse 80% 60% at 50% 30%, #000 30%, transparent 90%)",
        }}
      />

      {/* Top vignette */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(120% 80% at 50% 0%, transparent 40%, rgba(6,9,18,0.6) 100%)",
        }}
      />
    </div>
  );
}
