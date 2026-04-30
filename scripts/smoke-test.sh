#!/bin/bash
set -e

# Smoke test for MellyTrade Direction B (Sprint 1C)
# Runs mellytrade-api backend and frontend dev server, validates endpoints

BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo "Cleaning up..."
  [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
  [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true
  exit 1
}
trap cleanup EXIT

echo "Starting mellytrade-api (port 8000)..."
cd mellytrade_v3/mellytrade-api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ../..

echo "Waiting for backend to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend ready"
    break
  fi
  [ $i -eq 30 ] && echo "✗ Backend did not start" && exit 1
  sleep 1
done

echo "Starting frontend dev server (port 5173)..."
cd frontend
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo "Waiting for frontend to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✓ Frontend ready"
    break
  fi
  [ $i -eq 30 ] && echo "✗ Frontend did not start" && exit 1
  sleep 1
done

echo ""
echo "Running smoke tests..."
echo ""

# Test 1: Backend health endpoint
echo "Test 1: GET /health (backend safety posture)"
HEALTH=$(curl -s http://localhost:8000/health)
echo "$HEALTH" | jq .
if echo "$HEALTH" | jq -e '.dry_run == true' > /dev/null; then
  echo "✓ dry_run is enabled"
else
  echo "✗ dry_run is not enabled"
  exit 1
fi

# Test 2: Backend signals endpoint
echo ""
echo "Test 2: GET /signals (signal feed)"
SIGNALS=$(curl -s http://localhost:8000/signals?limit=5)
echo "$SIGNALS" | jq '.signals | length'
echo "✓ Signals endpoint reachable"

# Test 3: Audit feed endpoint
echo ""
echo "Test 3: GET /audit (audit feed)"
AUDIT=$(curl -s http://localhost:8000/audit?limit=5)
echo "$AUDIT" | jq '.events | length'
echo "✓ Audit endpoint reachable"

# Test 4: Risk config endpoint
echo ""
echo "Test 4: GET /risk/config (risk gates)"
RISK=$(curl -s http://localhost:8000/risk/config)
echo "$RISK" | jq '.max_risk_pct'
echo "✓ Risk config endpoint reachable"

# Test 5: Frontend dev proxy (via dev server)
echo ""
echo "Test 5: Frontend dev proxy /melly-api/health"
PROXY=$(curl -s http://localhost:5173/melly-api/health)
if echo "$PROXY" | jq -e '.dry_run == true' > /dev/null 2>&1; then
  echo "✓ Dev proxy working"
else
  echo "✗ Dev proxy failed or returned invalid JSON"
  exit 1
fi

echo ""
echo "✓ All smoke tests passed!"
trap - EXIT
cleanup
