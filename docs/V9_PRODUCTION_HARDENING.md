# Alpha AI Trading Terminal v9

Production-hardened fintech portfolio extension focused on:

- full WebSocket integration test suite
- structured JSON logging
- request IDs
- rate limiting
- MT5 health monitor
- safer execution queue foundation
- Cloud Run deploy pack
- GCP Secret Manager readiness
- local Windows + MT5 runbook

## Main additions

### Reliability
- persistent event replay endpoint
- replay-safe WebSocket flow
- stronger SQLite settings with WAL in the local artifact pack
- request-scoped IDs for easier tracing

### Security
- role-based dashboard access (`viewer`, `operator`, `admin`)
- rate limiting middleware
- Secret Manager deployment guidance

### Ops
- `/ops/mt5-health`
- Cloud Run deployment files
- Windows + MT5 operational runbook

### Testing
- WebSocket integration coverage
- auth role coverage
- replay coverage
- MT5 health endpoint coverage
- rate-limit unit coverage

## Portfolio positioning
This milestone makes the project look significantly closer to a production-minded fintech backend rather than a prototype or tutorial app.