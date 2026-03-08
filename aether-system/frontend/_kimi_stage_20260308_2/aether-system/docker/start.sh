#!/bin/bash

# AETHER System Startup Script

echo "🚀 Starting AETHER System..."

# Start nginx in background
echo "📡 Starting nginx..."
nginx

# Start backend API
echo "🔧 Starting backend API..."
cd /app/backend
python main.py &

# Wait for backend to be ready
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check health
echo "🏥 Checking system health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ AETHER System is running!"
    echo "🌐 Dashboard: http://localhost"
    echo "🔌 API: http://localhost:8000"
else
    echo "⚠️  Backend may still be starting..."
fi

# Keep container running
tail -f /var/log/nginx/access.log