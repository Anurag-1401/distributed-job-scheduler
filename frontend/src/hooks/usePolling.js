import { useEffect, useRef } from "react";

export function usePolling(callback, intervalMs, enabled = true) {
  const saved = useRef(callback);
  const running = useRef(false);

  useEffect(() => { saved.current = callback; }, [callback]);

  useEffect(() => {
    let cancelled = false;
    let timer;

    async function run() {
      if (cancelled || running.current) return;
      running.current = true;
      try { await saved.current?.(); } finally {
        running.current = false;
        if (!cancelled) timer = window.setTimeout(run, intervalMs);
      }
    }

    if (enabled && intervalMs > 0) run();
    return () => { cancelled = true; if (timer) window.clearTimeout(timer); };
  }, [intervalMs, enabled]);
}
