#!/bin/bash
# Docker build and deployment script for Trading Bot

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Trading Bot Docker Deployment ===${NC}"

# Parse arguments
BUILD_ONLY=false
PUSH=false
TAG="latest"
REGISTRY=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --build-only)
      BUILD_ONLY=true
      shift
      ;;
    --push)
      PUSH=true
      shift
      ;;
    --tag)
      TAG="$2"
      shift 2
      ;;
    --registry)
      REGISTRY="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check Docker installation
if ! command -v docker &> /dev/null; then
  echo -e "${RED}✗ Docker not found. Please install Docker.${NC}"
  exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
  echo -e "${RED}✗ Docker Compose not found. Please install Docker Compose.${NC}"
  exit 1
fi

IMAGE_NAME="grok-alpha-ai"
FULL_IMAGE_NAME="${REGISTRY:+$REGISTRY/}${IMAGE_NAME}:${TAG}"

echo -e "${YELLOW}Building image: ${FULL_IMAGE_NAME}${NC}"

# Build image
docker build \
  --tag "$FULL_IMAGE_NAME" \
  --tag "${REGISTRY:+$REGISTRY/}${IMAGE_NAME}:latest" \
  --file Dockerfile \
  .

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Build successful${NC}"
else
  echo -e "${RED}✗ Build failed${NC}"
  exit 1
fi

# Push to registry if requested
if [ "$PUSH" = true ] && [ -n "$REGISTRY" ]; then
  echo -e "${YELLOW}Pushing to registry: ${REGISTRY}${NC}"
  docker push "$FULL_IMAGE_NAME"
  docker push "${REGISTRY}/${IMAGE_NAME}:latest"
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Push successful${NC}"
  else
    echo -e "${RED}✗ Push failed${NC}"
    exit 1
  fi
fi

if [ "$BUILD_ONLY" = false ]; then
  echo -e "${YELLOW}Starting services with docker-compose...${NC}"
  docker-compose up -d trading-bot
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Services started${NC}"
    echo -e "${YELLOW}View logs:${NC}"
    echo "  docker-compose logs -f trading-bot"
  else
    echo -e "${RED}✗ Failed to start services${NC}"
    exit 1
  fi
fi

echo -e "${GREEN}=== Deployment Complete ===${NC}"
