// MellyTrade hub: relays signals from the FastAPI backend to the dashboard.
// - POST /api/publish  (secret-gated) stores each signal as an immutable KV item
// - GET  /api/signals  returns the latest N signals for the dashboard
// - GET  /api/health   liveness probe

export interface Env {
  SIGNALS: KVNamespace;
  CF_API_SECRET?: string;
  ALLOWED_ORIGIN?: string;
}

const SIGNAL_KEY_PREFIX = "signals:item:";
const MAX_SIGNALS = 50;
const MAX_TIMESTAMP_MS = 9999999999999;

function cors(env: Env) {
  const origin = env.ALLOWED_ORIGIN ?? "*";
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Hub-Secret",
  };
}

function json(body: unknown, init: ResponseInit & { env: Env }) {
  const { env, ...rest } = init;
  return new Response(JSON.stringify(body), {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...cors(env),
      ...(rest.headers ?? {}),
    },
  });
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors(env) });
    }

    if (url.pathname === "/api/health") {
      return json({ status: "ok", service: "mellytrade-hub" }, { env });
    }

    if (url.pathname === "/api/publish" && request.method === "POST") {
      if (env.CF_API_SECRET) {
        const provided = request.headers.get("X-Hub-Secret");
        if (provided !== env.CF_API_SECRET) {
          return json({ error: "unauthorized" }, { status: 401, env });
        }
      }
      const signal = await request.json().catch(() => null);
      if (!signal || typeof signal !== "object" || Array.isArray(signal)) {
        return json({ error: "invalid_json" }, { status: 400, env });
      }

      const stored = {
        ...(signal as Record<string, unknown>),
        received_at: new Date().toISOString(),
      };
      const key = signalKey();
      await env.SIGNALS.put(key, JSON.stringify(stored));
      return json({ status: "published", key }, { env });
    }

    if (url.pathname === "/api/signals" && request.method === "GET") {
      const list = await loadList(env);
      return json({ signals: list }, { env });
    }

    return json({ error: "not_found" }, { status: 404, env });
  },
};

async function loadList(env: Env): Promise<Record<string, unknown>[]> {
  const listed = await env.SIGNALS.list({
    prefix: SIGNAL_KEY_PREFIX,
    limit: MAX_SIGNALS,
  });
  const keys = listed.keys.map((item) => item.name);
  const values = await Promise.all(keys.map((key) => env.SIGNALS.get(key)));
  return values
    .map(parseSignal)
    .filter((value): value is Record<string, unknown> => value !== null);
}

function signalKey(): string {
  const reverseTimestamp = (MAX_TIMESTAMP_MS - Date.now())
    .toString()
    .padStart(13, "0");
  return `${SIGNAL_KEY_PREFIX}${reverseTimestamp}:${crypto.randomUUID()}`;
}

function parseSignal(raw: string | null): Record<string, unknown> | null {
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed)
      ? (parsed as Record<string, unknown>)
      : null;
  } catch {
    return null;
  }
}
