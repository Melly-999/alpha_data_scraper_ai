import { useEffect, useRef, useState } from "react";

export function usePollingResource<T>(
  loader: () => Promise<T>,
  intervalMs: number,
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // Wall-clock of the most recent successful fetch. Pages can use this to
  // render "Last updated …" labels so operators can see at a glance when a
  // panel last received fresh data — important for a passive read-only
  // terminal where staleness is the main failure mode.
  const [lastUpdatedAt, setLastUpdatedAt] = useState<Date | null>(null);
  const loaderRef = useRef(loader);

  // Keep the latest loader without restarting the polling loop on each render.
  loaderRef.current = loader;

  useEffect(() => {
    let cancelled = false;
    let timer: number | undefined;

    const tick = async () => {
      try {
        const next = await loaderRef.current();
        if (!cancelled) {
          setData(next);
          setError(null);
          setLastUpdatedAt(new Date());
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Unknown error");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
          timer = window.setTimeout(tick, intervalMs);
        }
      }
    };

    void tick();

    return () => {
      cancelled = true;
      if (timer) {
        window.clearTimeout(timer);
      }
    };
  }, [intervalMs]);

  return { data, loading, error, lastUpdatedAt };
}

