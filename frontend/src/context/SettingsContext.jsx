import { createContext, useContext, useMemo, useState } from "react";

const KEY = "scheduler.poll_interval_ms";
const SettingsContext = createContext(null);

export function SettingsProvider({ children }) {
  const [pollIntervalMs, setPollIntervalMsState] = useState(() => {
    const stored = Number(localStorage.getItem(KEY));
    return stored > 0 ? stored : 10000;
  });

  const value = useMemo(
    () => ({
      pollIntervalMs,
      setPollIntervalMs(ms) {
        setPollIntervalMsState(ms);
        localStorage.setItem(KEY, String(ms));
      },
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
    }),
    [pollIntervalMs]
  );

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings() {
  const ctx = useContext(SettingsContext);
  if (!ctx) {
    throw new Error("useSettings must be used within SettingsProvider");
  }
  return ctx;
}
