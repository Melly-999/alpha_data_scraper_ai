// Typed FastAPI client used by every hook in `frontend/src/hooks` and
// the Risk Manager / Trade Blotter pages. Read-only by default; the
// only mutation calls in the app are existing risk-control endpoints
// (`/risk/config`, `/risk/emergency-stop`) - this module does not
// expose any new endpoint and never places trading orders.

const RAW_BASE = (import.meta.env.VITE_API_BASE_URL ?? "/api") as string;
const API_BASE = RAW_BASE.replace(/\/+$/, "");

function joinUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) {
    return path;
  }
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE}${suffix}`;
}

async function parseError(response: Response): Promise<string> {
  const fallback = `${response.status} ${response.statusText}`;
  try {
    const text = await response.text();
    if (!text) {
      return fallback;
    }
    try {
      const parsed = JSON.parse(text);
      if (parsed && typeof parsed === "object" && "detail" in parsed) {
        const detail = (parsed as { detail: unknown }).detail;
        if (typeof detail === "string" && detail.length > 0) {
          return detail;
        }
      }
    } catch {
      // not JSON, fall through to text
    }
    return text.length > 240 ? `${text.slice(0, 240)}...` : text;
  } catch {
    return fallback;
  }
}

async function request<T>(
  method: "GET" | "POST" | "PUT",
  path: string,
  body?: unknown,
): Promise<T> {
  const init: RequestInit = {
    method,
    headers: { Accept: "application/json" },
    credentials: "same-origin",
  };
  if (body !== undefined) {
    init.body = JSON.stringify(body);
    init.headers = {
      ...(init.headers as Record<string, string>),
      "Content-Type": "application/json",
    };
  }

  const response = await fetch(joinUrl(path), init);
  if (!response.ok) {
    throw new Error(await parseError(response));
  }

  if (response.status === 204) {
    return undefined as unknown as T;
  }
  return (await response.json()) as T;
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>("GET", path);
}

export function apiPost<TResponse, TBody = unknown>(
  path: string,
  body?: TBody,
): Promise<TResponse> {
  return request<TResponse>("POST", path, body);
}

export function apiPut<TResponse, TBody = unknown>(
  path: string,
  body: TBody,
): Promise<TResponse> {
  return request<TResponse>("PUT", path, body);
}
