import React from "react";

// Shared in-memory store for the candidate + session, persisted to sessionStorage
// so a refresh during a demo doesn't wipe the interview state.

const KEY = "abtalks_session_v1";

const CandidateContext = React.createContext(null);

export function CandidateProvider({ children }) {
  const [state, setState] = React.useState(() => {
    try {
      const raw = sessionStorage.getItem(KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  const setSession = React.useCallback((next) => {
    setState((prev) => {
      const merged = typeof next === "function" ? next(prev) : next;
      try {
        if (merged) sessionStorage.setItem(KEY, JSON.stringify(merged));
        else sessionStorage.removeItem(KEY);
      } catch {
        /* ignore */
      }
      return merged;
    });
  }, []);

  const clear = React.useCallback(() => setSession(null), [setSession]);

  const value = React.useMemo(
    () => ({ session: state, setSession, clear }),
    [state, setSession, clear]
  );

  return <CandidateContext.Provider value={value}>{children}</CandidateContext.Provider>;
}

export function useCandidate() {
  const ctx = React.useContext(CandidateContext);
  if (!ctx) throw new Error("useCandidate must be used within CandidateProvider");
  return ctx;
}
