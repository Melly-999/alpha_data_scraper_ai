export interface Env {
  TRADING_HUB: DurableObjectNamespace;
  CF_API_SECRET: string;
  ASSETS: Fetcher;
}

export class TradingHub {
  constructor(private state: DurableObjectState, private env: Env) {}

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === '/ws') {
      const pair = new WebSocketPair();
      const [client, server] = Object.values(pair);
      this.state.acceptWebSocket(server);
      return new Response(null, { status: 101, webSocket: client });
    }
    if (url.pathname === '/publish' && request.method === 'POST') {
      const body = await request.text();
      this.state.getWebSockets().forEach((ws) => {
        try { ws.send(body); } catch {}
      });
      return Response.json({ status: 'ok', delivered: this.state.getWebSockets().length });
    }
    return new Response('Not found', { status: 404 });
  }

  webSocketMessage(ws: WebSocket, message: string | ArrayBuffer) {
    if (typeof message === 'string' && message.includes('ping')) {
      ws.send(JSON.stringify({ type: 'pong' }));
    }
  }
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === '/api/publish' && request.method === 'POST') {
      const secret = request.headers.get('X-API-Secret') || '';
      if (secret !== env.CF_API_SECRET) {
        return Response.json({ error: 'Unauthorized' }, { status: 401 });
      }
      const id = env.TRADING_HUB.idFromName('global');
      const stub = env.TRADING_HUB.get(id);
      return stub.fetch('https://hub/publish', { method: 'POST', body: await request.text() });
    }
    if (url.pathname === '/ws') {
      const id = env.TRADING_HUB.idFromName('global');
      const stub = env.TRADING_HUB.get(id);
      return stub.fetch(request);
    }
    return env.ASSETS.fetch(request);
  }
};
