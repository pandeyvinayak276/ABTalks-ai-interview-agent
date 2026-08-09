import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import AuroraBackground from "./components/AuroraBackground.jsx";
import Landing from "./pages/Landing.jsx";
import Setup from "./pages/Setup.jsx";
import Interview from "./pages/Interview.jsx";
import Results from "./pages/Results.jsx";
import DownloadPage from "./pages/Download.jsx";

export default function App() {
  return (
    <>
      <AuroraBackground />
      <main style={{ position: "relative", zIndex: 1, minHeight: "100vh" }}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/setup" element={<Setup />} />
          <Route path="/interview" element={<Interview />} />
          <Route path="/results" element={<Results />} />
          <Route path="/download" element={<DownloadPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </>
  );
}
