# Datadog Setup for MellyTrade

Datadog is optional observability for the read-only MellyTrade terminal. It does not change trading behavior, does not enable live execution, and must never receive broker credentials.

## What Datadog Gives MellyTrade

- Host metrics for CPU, memory, disk, and process health
- Docker container logs from staging and integration environments
- FastAPI traces and APM timing for request paths
- Dashboards for API health, latency, and error rate
- Alerts for degradations and restarts
- MCP access for AI-assisted debugging through Claude Code or Codex

## Which Install Tile To Choose

- Docker: use this for BytePlus, VPS, or any Docker Compose staging host
- Linux: use this for a non-containerized VM
- Kubernetes: use only when there is a real Kubernetes cluster to observe

### Render vs VPS / BytePlus

- Render (and similar managed PaaS): you generally cannot run a co-located host
  agent or mount the Docker socket, so the Docker/host-agent tile does not apply.
  Use application-level APM with `ddtrace` pointing at Datadog's intake, or an
  agentless log forwarder, and skip `docker-compose.observability.yml`. Treat
  Render as observe-via-app-only.
- VPS / BytePlus Docker host: you own the host, so you can run the sidecar
  `datadog-agent` with the read-only Docker socket mount and collect container
  logs, host metrics, and APM. This is the full-fidelity option and what the
  compose override targets.

## Safe Setup Steps

1. Create a Datadog API key in the Datadog UI.
2. Export `DD_API_KEY` locally or on the staging host.
3. Start the agent with the compose override:

```bash
docker compose -f docker-compose.yml -f docker-compose.observability.yml up -d datadog-agent
```

4. Confirm the agent is healthy:

```bash
docker compose logs -f datadog-agent
docker compose exec datadog-agent agent status
```

5. Confirm logs arrive in Datadog.
6. Keep the main app runnable without Datadog. Observability must stay optional.

## FastAPI APM

- Add `ddtrace` only if you choose to instrument the API safely
- Run the app with `ddtrace-run` only when you intentionally want traces
- Set `DD_AGENT_HOST=datadog-agent`
- Keep local development and tests working without Datadog
- Do not make Datadog a required runtime dependency for the terminal

Example:

```bash
DD_AGENT_HOST=datadog-agent DD_TRACE_AGENT_PORT=8126 ddtrace-run python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

## Suggested Monitors

- API health endpoint unavailable
- 5xx error rate increases
- High latency on critical endpoints
- Container restart loop
- CPU, memory, or disk pressure

Suggested thresholds should start conservative and alert on sustained degradation rather than short spikes.

## Health Endpoints To Monitor

- `/health`
- `/api/health`
- `/api/safety/status`
- `/api/terminal/summary` if present
- `/api/paper/run/preview` if present

## Datadog MCP

Datadog MCP gives AI agents read-only access to observability data for debugging, incident triage, and dashboard inspection. It is for observe-first workflows only.

Claude Code example:

```bash
claude mcp add --transport http datadog https://mcp.datadoghq.eu/api/unstable/mcp-server/mcp
```

Codex example:

```toml
[mcp_servers.datadog]
type = "http"
url = "https://mcp.datadoghq.eu/api/unstable/mcp-server/mcp"
```

If you use a non-EU Datadog site, change the endpoint to match the site selector in the Datadog UI.

## Security

- Never send broker credentials to Datadog
- Do not log API keys, passwords, tokens, or account IDs
- Sanitize request and response bodies before logging
- Avoid PII and other sensitive personal data in logs
- Do not use cloud observability to trigger live trading
- Keep the observability stack separate from execution paths
