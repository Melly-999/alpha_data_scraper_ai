import { useEffect, useRef, useState } from "react";

export function usePollingResource<T>(
  loader: () => Promise<T>,
  intervalMs: number,
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
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

  return { data, loading, error };
}

