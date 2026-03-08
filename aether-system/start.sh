#!/bin/bash

# AETHER Quick Start Script
# Run this to get started immediately

echo "AETHER System Quick Start"
echo "=============================="
echo ""

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    echo "Podman not found. Please install Podman first:"
    echo "   https://podman.io/docs/installation"
    exit 1
fi

# Check if podman-compose is installed
COMPOSE_CMD=""
if command -v podman-compose &> /dev/null; then
    COMPOSE_CMD="podman-compose"
elif python -m podman_compose version &> /dev/null; then
    COMPOSE_CMD="python -m podman_compose"
else
    echo "podman-compose not found. Please install podman-compose:"
    echo "   pip install podman-compose"
    exit 1
fi

echo "Podman + podman-compose found"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Created .env file"
    echo "Edit .env and add your NASA API key (optional)"
    echo ""
fi

# Create data directories
echo "Creating data directories..."
mkdir -p data uploads ai_models/cache vector_db
echo "Directories created"
echo ""

# Start mode
UP_CMD="up -d"
if [ "$1" = "--build" ]; then
    UP_CMD="up -d --build"
fi

echo "Starting AETHER with podman-compose..."
if [ "$1" = "--build" ]; then
    echo "Rebuild enabled (this can take several minutes)."
else
    echo "Using existing images/dependencies (fast start)."
fi
echo ""
eval "$COMPOSE_CMD $UP_CMD"

echo ""
echo "Waiting for services to start..."
sleep 10

# Check health
echo "Checking system health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo "AETHER is running."
    echo ""
    echo "Access your system:"
    echo "   Dashboard: http://localhost:3000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo "   Health:    http://localhost:8000/health"
    echo ""
    echo "View logs:"
    echo "   $COMPOSE_CMD logs -f"
    echo ""
    echo "Stop system:"
    echo "   $COMPOSE_CMD down"
    echo ""
else
    echo ""
    echo "System still initializing."
    echo "   Check logs: $COMPOSE_CMD logs -f"
    echo ""
    echo "Once ready, access:"
    echo "   Dashboard: http://localhost:3000"
    echo "   API Docs:  http://localhost:8000/docs"
    echo ""
fi
