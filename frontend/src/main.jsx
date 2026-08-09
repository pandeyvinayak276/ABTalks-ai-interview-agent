import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import { CandidateProvider } from "./state/candidate.jsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <CandidateProvider>
        <App />
      </CandidateProvider>
    </BrowserRouter>
  </React.StrictMode>
);
