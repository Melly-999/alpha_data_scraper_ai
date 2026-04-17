# Trading Bot Deployment Guide

Complete guide for deploying the Grok Alpha AI Trading Bot in various environments.

## MellyTrade v3 Deployment Notes

`mellytrade_v3/` now contains the integrated signal flow:

1. MT5 bridge creates a weighted technical/LSTM signal.
2. FastAPI `app.main:app` validates `X-API-Key`, risk percent, confidence,
   SL/TP, and cooldown.
3. Accepted and blocked signals are persisted in SQLAlchemy `signal_logs`.
4. Accepted signals are published to the Cloudflare Worker `/api/publish`
   endpoint.
5. Dashboard clients receive live signals over the Worker `/ws` WebSocket.

### Local Windows Commands

```powershell
# Worker hub
cd C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai\mellytrade_v3\mellytrade
npm install
npm run dev

# Backend
cd C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai\mellytrade_v3\mellytrade-api
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload

# Dashboard
cd C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai\mellytrade_v3\mellytrade\dashboard
npm install
npm run dev

# MT5 bridge
cd C:\AI\MellyTrade_Workspace\02_Repo\alpha_data_scraper_ai\mellytrade_v3\mt5
..\mellytrade-api\.venv\Scripts\python.exe mt5_bridge.py
```

### Required Environment

Use `mellytrade_v3/mellytrade-api/.env` for backend settings:

```env
DATABASE_URL=sqlite:///./signals.db
FASTAPI_KEY=change-me-fastapi-key
CF_HUB_URL=http://127.0.0.1:8787
CF_API_SECRET=change-me-cloudflare-secret
COOLDOWN_SECONDS=120
MIN_CONFIDENCE=70
MAX_RISK_PERCENT=1.0
```

For production, replace SQLite with a Postgres `DATABASE_URL`, rotate both API
secrets, and provide real `CLOUDMCP_*_URL` and `CLOUDMCP_*_TOKEN` values through
system environment variables or `.env`.

### Validation Checklist

- `python -m pytest -q` in `mellytrade_v3/mellytrade-api`
- `python -m pytest -q tests` in `mellytrade_v3/mt5`
- `npm run build` in `mellytrade_v3/mellytrade/dashboard`
- Manual `GET /health`
- Manual `POST /signal` checks for unauthorized, accepted, max risk,
  confidence, missing SL/TP, and cooldown cases
- Confirm `signal_logs` contains both accepted and blocked signals

## Table of Contents

1. [Windows Service (Local Deployment)](#windows-service-local-deployment)
2. [Docker Deployment (Linux/Cloud)](#docker-deployment-linuxcloud)
3. [Docker Compose (Multi-Service)](#docker-compose-multi-service)
4. [Production Checklist](#production-checklist)
5. [Monitoring & Logs](#monitoring--logs)
6. [Troubleshooting](#troubleshooting)

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
