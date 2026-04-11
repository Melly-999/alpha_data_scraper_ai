#!/bin/bash
# build_and_run.sh - Alpha AI Docker automation

echo "🚀 Alpha AI - Docker Build & Run"
echo "================================="

# 1. Sprawdzenie czy Docker jest zainstalowany
if ! command -v docker &> /dev/null; then
    echo "❌ Docker nie jest zainstalowany!"
    echo "Pobierz z https://docker.com"
    exit 1
fi

# 2. Sprawdzenie docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose nie znaleziony - próbuję z docker compose..."
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# 3. Tworzenie .env jeśli nie istnieje
if [ ! -f .env ]; then
    echo "📝 Tworzę plik .env (wpisz API key potem)..."
    cp .env.example .env
    echo "⚠️  EDYTUJ .env i wpisz ANTHROPIC_API_KEY"
    echo "Następnie uruchom ponownie: ./build_and_run.sh"
    exit 0
fi

# 4. Budowanie
echo ""
echo "🔨 Building Docker images..."
$DOCKER_COMPOSE build --no-cache

# 5. Uruchamianie
echo ""
echo "▶️  Starting services..."
$DOCKER_COMPOSE up -d

# 6. Status
echo ""
echo "📊 Services status:"
$DOCKER_COMPOSE ps

# 7. Logi
echo ""
echo "📜 Scheduler logs (ostatnie 20 linii):"
$DOCKER_COMPOSE logs --tail=20 alpha-ai-scheduler

echo ""
echo "✅ Alpha AI is running!"
echo ""
echo "📍 Webhook: http://localhost:8000/webhook"
echo "📍 Health: http://localhost:8000/health"
echo ""
echo "Commands:"
echo "  Logi scheduler:  docker-compose logs -f alpha-ai-scheduler"
echo "  Logi webhook:    docker-compose logs -f alpha-ai-webhook"
echo "  Stop:            docker-compose down"
echo "  Restart:         docker-compose restart"
