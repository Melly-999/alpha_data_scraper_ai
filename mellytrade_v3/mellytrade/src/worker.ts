// MellyTrade hub: relays signals from the FastAPI backend to the dashboard.
// - POST /api/publish  (secret-gated) stores the signal in KV + latest slot
// - GET  /api/signals  returns the latest N signals for the dashboard
// - GET  /api/health   liveness probe

export interface Env {
  SIGNALS: KVNamespace;
  CF_API_SECRET?: string;
  ALLOWED_ORIGIN?: string;
}

const LATEST_KEY = "signals:latest";
const MAX_SIGNALS = 50;

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
      if (!signal) return json({ error: "invalid_json" }, { status: 400, env });

      const list = await loadList(env);
      list.unshift(signal as Record<string, unknown>);
      const trimmed = list.slice(0, MAX_SIGNALS);
      await env.SIGNALS.put(LATEST_KEY, JSON.stringify(trimmed));
      return json({ status: "published", count: trimmed.length }, { env });
    }

    if (url.pathname === "/api/signals" && request.method === "GET") {
      const list = await loadList(env);
      return json({ signals: list }, { env });
    }

    return json({ error: "not_found" }, { status: 404, env });
  },
};

async function loadList(env: Env): Promise<Record<string, unknown>[]> {
  const raw = await env.SIGNALS.get(LATEST_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}
