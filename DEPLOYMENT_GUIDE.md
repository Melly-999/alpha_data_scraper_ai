# Trading Bot Deployment Guide

Complete guide for deploying the Grok Alpha AI Trading Bot in various environments.

## Table of Contents

1. [Windows Service (Local Deployment)](#windows-service-local-deployment)
2. [Docker Deployment (Linux/Cloud)](#docker-deployment-linuxcloud)
3. [Docker Compose (Multi-Service)](#docker-compose-multi-service)
4. [MellyTrade v3 stack](#mellytrade-v3-stack)
5. [Production Checklist](#production-checklist)
6. [Monitoring & Logs](#monitoring--logs)
7. [Troubleshooting](#troubleshooting)

## MellyTrade v3 stack

The `mellytrade_v3/` sub-project bundles four cooperating pieces:

- **Backend** — `mellytrade_v3/mellytrade-api/` (FastAPI)
- **MT5 bridge** — `mellytrade_v3/mt5/`
- **Cloudflare Worker hub** — `mellytrade_v3/mellytrade/`
- **React dashboard** — `mellytrade_v3/mellytrade/dashboard/`

### Required environment

Create `mellytrade_v3/mellytrade-api/.env` from the `.env.example`:

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | SQLite default; Postgres in prod |
| `FASTAPI_KEY` | Required `X-API-Key` header for `/signal`, `/signals` |
| `CF_HUB_URL` | Worker `/api/publish` URL |
| `CF_API_SECRET` | Shared secret between backend and worker |
| `COOLDOWN_SECONDS` | Per-symbol cooldown (default 60) |
| `MIN_CONFIDENCE` | Minimum accepted confidence (default 70) |
| `MAX_RISK_PERCENT` | Hard cap on `risk_percent` (default 1.0) |
| `ALPHA_REPO_PATH` | Absolute path to this repo (so MT5 bridge can import the LSTM) |
| `ALPHA_LSTM_CLASS` | Defaults to `lstm_model.LSTMPipeline` |
| `ALPHA_LSTM_FUNCTION` | Optional override for the callable |

### Local run

```bash
# Backend (uvicorn, port 8000 or 8001 if 8000 is busy)
cd mellytrade_v3/mellytrade-api
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
pytest -q                     # 7 passing
uvicorn app.main:app --reload --port 8000
# or: uvicorn app.main:app --reload --port 8001

# Cloudflare Worker
cd ../mellytrade
npm install
npm run dev                   # http://127.0.0.1:8787

# Dashboard
cd dashboard
npm install
npm run dev                   # http://127.0.0.1:5173
npm audit fix                 # resolve moderate advisories when possible
```

### Risk rules (enforced, never loosened)

- `confidence >= 70` — rejected with `confidence_below_min`
- `risk_percent <= 1.0` — rejected with `risk_above_max`
- SL and TP required and consistent with the direction
- Per-symbol cooldown of `COOLDOWN_SECONDS` — rejected with `cooldown_active`

### Tests

- Backend: `cd mellytrade_v3/mellytrade-api && pytest -q` (7 tests)
- MT5 bridge: `cd mellytrade_v3 && pytest mt5/tests -q` (3 tests)

### Open production items

- Provision a Postgres `DATABASE_URL` (e.g. Cloud SQL).
- Rotate `FASTAPI_KEY`, `CF_API_SECRET` and real CloudMCP tokens (see
  `.mcp.json` / `.cursor/mcp.json`).
- Deploy backend via docker-compose or Cloud Run (image built from
  `mellytrade-api/`).

---

## Windows Service (Local Deployment)

Run the trading bot as a Windows Service for automatic startup and monitoring.

### Prerequisites

- Windows 7 or later
- Python 3.10+
- Administrator privileges
- NSSM (Non-Sucking Service Manager) - Optional but recommended

### Installation Steps

#### Step 1: Install NSSM (Recommended)

Download from: https://nssm.cc/download

```powershell
# Extract NSSM and add to PATH
# Or use in scripts with full path
```

#### Step 2: Create Virtual Environment

```powershell
# From project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Step 3: Install Service

```powershell
# Run as Administrator
powershell -ExecutionPolicy Bypass -File install_windows_service.ps1
```

This will:
- Create wrapper script
- Install service (using NSSM or sc.exe)
- Configure auto-restart
- Set startup type to automatic

#### Step 4: Start Service

```powershell
# Option 1: PowerShell
powershell -File install_windows_service.ps1 -Start

# Option 2: Services Manager
services.msc  # Find "Grok Alpha AI Trading Bot"
# Right-click → Start

# Option 3: Net command
net start GrokAlphaAI
```

### Service Management

```powershell
# Show status
powershell -File install_windows_service.ps1 -Status

# Stop service
powershell -File install_windows_service.ps1 -Stop
# Or: net stop GrokAlphaAI

# View logs
# Logs are in: service_logs\GrokAlphaAI.log (if using NSSM)
```

### Configuration

Edit `config.json` before starting service:

```json
{
  "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
  "timeframes": ["M1", "M5", "H1"],
  "weights": {
    "M1": 0.4,
    "M5": 0.35,
    "H1": 0.25
  },
  "balance": 1000.0,
  "risk_per_trade": 0.02,
  "demo_mode": true
}
```

### Troubleshooting Windows Service

```powershell
# View service details
Get-Service -Name GrokAlphaAI

# View detailed status
sc.exe query GrokAlphaAI

# View event logs
Get-EventLog -LogName System -Source ServiceName | Select-Object -Last 10

# Restart service
Restart-Service -Name GrokAlphaAI
```

---

## Docker Deployment (Linux/Cloud)

### Building Docker Image

```bash
# Build locally
./docker-build.sh

# Build with custom tag
./docker-build.sh --tag v1.0.0

# Build and push to registry
./docker-build.sh --push --registry docker.io/username --tag v1.0.0
```

### Running Container

```bash
# Run directly
docker run -d \
  --name trading-bot \
  -e CLAUDE_API_KEY=your_key \
  -e NEWSAPI_KEY=your_key \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/config.json:/app/config.json:ro \
  grok-alpha-ai:latest

# Follow logs
docker logs -f trading-bot

# Stop container
docker stop trading-bot
```

### Container Environment Variables

```bash
CLAUDE_API_KEY      # Anthropic API key for signal validation
NEWSAPI_KEY         # NewsAPI key for sentiment analysis
TZ                  # Timezone (default: UTC)
PYTHONUNBUFFERED    # Set to 1 (enabled by default in Dockerfile)
```

### Volume Mounts

```bash
# /app/logs        # Application logs
# /app/data        # Persistent data
# /app/backups     # Trade backups
# /app/config.json # Configuration file
```

---

## Docker Compose (Multi-Service)

Run complete stack with trading bot, tests, and Jupyter notebook.

### Setup

```bash
# Create .env file
cat > .env << EOF
CLAUDE_API_KEY=your_claude_key
NEWSAPI_KEY=your_newsapi_key
TZ=UTC
EOF

# Build all services
docker-compose build

# Start main service
docker-compose up -d trading-bot

# View logs
docker-compose logs -f trading-bot
```

### Services Available

#### 1. Trading Bot (Main Service)

```bash
# Start
docker-compose up -d trading-bot

# Logs
docker-compose logs -f trading-bot

# Stop
docker-compose down trading-bot
```

#### 2. Test Runner

```bash
# Run tests
docker-compose run --rm test-runner

# With specific test file
docker-compose run --rm test-runner python -m pytest tests/test_integration_advanced.py -v
```

#### 3. Development Shell

```bash
# Open interactive shell
docker-compose run --rm dev-shell

# Run commands
docker-compose run --rm dev-shell python example_runner.py --symbols EURUSD
```

#### 4. Jupyter Notebook

```bash
# Start Jupyter
docker-compose up -d jupyter

# Access at http://localhost:8888
# Get token from logs
docker-compose logs jupyter | grep token
```

### Managing Services

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View all services
docker-compose ps

# View service logs
docker-compose logs [service_name]

# Follow specific service logs
docker-compose logs -f trading-bot

# Restart service
docker-compose restart trading-bot

# Remove all containers and volumes
docker-compose down -v
```

---

## Production Checklist

### Before Deployment

- [ ] **Configuration**
  - [ ] Set realistic symbols and timeframes
  - [ ] Configure risk parameters (risk_per_trade)
  - [ ] Set balance according to account
  - [ ] Disable demo_mode for live trading (carefully!)

- [ ] **API Keys**
  - [ ] Set CLAUDE_API_KEY environment variable
  - [ ] Set NEWSAPI_KEY environment variable
  - [ ] Verify API keys have proper permissions

- [ ] **Testing**
  - [ ] Run unit tests: `pytest tests/ -v`
  - [ ] Run integration tests: `pytest tests/test_integration_advanced.py -v`
  - [ ] Backtest strategy: `python example_runner.py --demo`
  - [ ] Paper trading (demo mode): 24+ hours

- [ ] **Monitoring**
  - [ ] Set up log aggregation
  - [ ] Configure alerts for errors
  - [ ] Monitor resource usage (CPU, memory)
  - [ ] Track trade execution

- [ ] **Security**
  - [ ] Rotate API keys periodically
  - [ ] Use strong passwords for MT5
  - [ ] Run container with non-root user (already configured)
  - [ ] Use secrets management (Docker Secrets, Kubernetes Secrets)
  - [ ] Restrict network access to bot

- [ ] **Backup & Recovery**
  - [ ] Daily backups of /app/data and /app/backups
  - [ ] Store configuration separately
  - [ ] Test restore procedure
  - [ ] Document recovery process

### Windows Service Deployment

```powershell
# 1. Install .NET runtime if needed
# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

# 3. Configure config.json
# 4. Install service
powershell -ExecutionPolicy Bypass -File install_windows_service.ps1

# 5. Start service
net start GrokAlphaAI

# 6. Verify
powershell -File install_windows_service.ps1 -Status
```

### Docker Deployment

```bash
# 1. Build and push image
./docker-build.sh --push --registry your-registry --tag v1.0.0

# 2. Deploy to Kubernetes or Docker host
docker pull your-registry/grok-alpha-ai:v1.0.0
docker run -d \
  --name trading-bot \
  --restart unless-stopped \
  -e CLAUDE_API_KEY=$CLAUDE_API_KEY \
  -e NEWSAPI_KEY=$NEWSAPI_KEY \
  -v logs:/app/logs \
  -v data:/app/data \
  your-registry/grok-alpha-ai:v1.0.0

# 3. Monitor application
docker logs -f trading-bot
```

---

## Monitoring & Logs

### Application Logs

```bash
# Windows Service logs
Get-Content -Path "service_logs\GrokAlphaAI.log" -Tail 100

# Docker logs
docker logs -f trading-bot

# Docker Compose logs
docker-compose logs -f trading-bot
```

### Log Locations

| Environment | Log Path |
|---|---|
| Windows Service | `service_logs\GrokAlphaAI.log` |
| Local Python | `logs\trading_pipeline.log` |
| Docker | `/app/logs/` (inside container) |
| Docker Compose | `./logs/` (mounted volume) |

### Log Levels

Configure in `logging.basicConfig()`:
- `DEBUG`: Detailed information
- `INFO`: General information
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical issues

### Health Checks

#### Windows Service
```powershell
# Check service status
Get-Service -Name GrokAlphaAI

# Check process
Get-Process | Where-Object {$_.ProcessName -like "*python*"}
```

#### Docker
```bash
# Container health
docker inspect --format='{{json .State.Health}}' trading-bot | jq .

# Container logs
docker logs trading-bot

# Resource usage
docker stats trading-bot
```

---

## Troubleshooting

### Windows Service Issues

**Service won't start**
```powershell
# Check service details
sc.exe query GrokAlphaAI

# Check event logs
Get-EventLog -LogName System -Source ServiceName | Select-Object -Last 10

# Try running manually
powershell -ExecutionPolicy Bypass -File service_wrapper.ps1
```

**Python not found**
```powershell
# Verify Python in venv
.\.venv\Scripts\python.exe --version

# Reinstall venv
python -m venv .venv --clear
.\.venv\Scripts\pip install -r requirements.txt
```

**Permission denied**
```powershell
# Run PowerShell as Administrator
# Or change service account:
sc.exe config GrokAlphaAI obj= ".\YourUsername" password= "YourPassword"
```

### Docker Issues

**Container exits immediately**
```bash
# Check logs
docker logs trading-bot

# Run debug container
docker run -it grok-alpha-ai:latest /bin/bash

# Test command
docker run -it grok-alpha-ai:latest python example_runner.py --help
```

**Out of memory**
```bash
# Check memory usage
docker stats trading-bot

# Increase memory limit
docker update --memory 2g trading-bot
```

**Network issues**
```bash
# Check network connectivity
docker exec trading-bot ping -c 1 8.8.8.8

# Check DNS
docker exec trading-bot nslookup api.anthropic.com
```

### Common Errors

**`CLAUDE_API_KEY not set`**
```bash
# Set environment variable
export CLAUDE_API_KEY=your_key
docker-compose up
# Or in .env file
echo "CLAUDE_API_KEY=your_key" >> .env
```

**`MetaTrader5 not available`**
```bash
# MT5 is Windows-only, bot will use mock data on Linux
# For real MT5 on Linux, use wine+MT5 or MT5 API bridge
```

**`Port already in use`**
```bash
# Change port mapping in docker-compose.yml
ports:
  - "8001:8000"  # Change from 8000 to 8001
```

---

## Contact & Support

For issues or questions:
- Check logs: `logs/trading_pipeline.log`
- Review configuration: `config.json`
- Run tests: `pytest tests/`
- Check GitHub: [Project Repository]

---

**Last Updated:** 2026-03-27  
**Version:** 1.0.0
