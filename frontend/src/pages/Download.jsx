import React from "react";

function DownloadIcon({ size = 20 }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );
}

export default function DownloadPage() {
  return (
    <div style={{ maxWidth: 720, margin: "120px auto", padding: "0 24px", textAlign: "center" }}>
      <h1 style={{ fontSize: 32, fontWeight: 700, marginBottom: 16 }}>
        Download ABTalks Frontend
      </h1>
      <p style={{ fontSize: 16, lineHeight: 1.6, marginBottom: 40 }}>
        Click the button below to download the complete frontend source as a ZIP file.
        After it downloads, extract it and open the folder in VS Code.
      </p>
      <a
        href="/abtalks-frontend.zip"
        download="abtalks-frontend.zip"
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 10,
          padding: "14px 32px",
          background: "#2563eb",
          color: "#ffffff",
          textDecoration: "none",
          borderRadius: 8,
          fontSize: 16,
          fontWeight: 600,
        }}
      >
        <DownloadIcon size={20} />
        Download abtalks-frontend.zip
      </a>
      <div style={{ marginTop: 56, textAlign: "left", background: "#f8fafc", borderRadius: 12, padding: 24 }}>
        <h2 style={{ fontSize: 18, marginBottom: 12 }}>What's inside the ZIP:</h2>
        <ul style={{ lineHeight: 1.8, paddingLeft: 20, fontSize: 14 }}>
          <li>package.json</li>
          <li>package-lock.json</li>
          <li>index.html</li>
          <li>vite.config.js</li>
          <li>src/App.jsx, src/main.jsx, src/index.css</li>
          <li>src/pages/ — Landing, Setup, Interview, Results</li>
          <li>src/components/ — Header, AuroraBackground, ui</li>
          <li>src/api/interviewApi.js</li>
          <li>src/state/candidate.jsx</li>
          <li>README.md</li>
        </ul>
      </div>
    </div>
  );
}
