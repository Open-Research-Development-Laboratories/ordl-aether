#!/bin/bash

# AETHER Quick Start Script
# Run this to get started immediately

echo "🚀 AETHER System Quick Start"
echo "=============================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker found"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your NASA API key (optional)"
    echo "   Get free key at: https://api.nasa.gov"
    echo ""
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data uploads ai_models/cache vector_db
echo "✅ Directories created"
echo ""

# Build and start
echo "🔨 Building and starting AETHER..."
echo "   (This may take 5-10 minutes on first run)"
echo ""
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check health
echo "🏥 Checking system health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo "✅ AETHER is running!"
    echo ""
    echo "🌐 Access your system:"
    echo "   Dashboard: http://localhost"
    echo "   API Docs:  http://localhost:8000/docs"
    echo "   Health:    http://localhost:8000/health"
    echo ""
    echo "📊 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop system:"
    echo "   docker-compose down"
    echo ""
else
    echo ""
    echo "⏳ System still initializing..."
    echo "   Check logs: docker-compose logs -f"
    echo ""
    echo "🌐 Once ready, access:"
    echo "   Dashboard: http://localhost"
    echo "   API Docs:  http://localhost:8000/docs"
    echo ""
fi