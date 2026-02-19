#!/bin/bash
# Digital Twins Platform - Quick Start Script

set -e

echo "🏭 Digital Twins Platform - Quick Start"
echo "========================================"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is required but not installed."
    exit 1
fi

echo "✅ Docker is available"

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Digital Twins Platform Configuration
DITTO_VERSION=3.8.0
OPENAI_API_KEY=your-openai-api-key-here
LOG_LEVEL=INFO
EOF
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY for AI features"
fi

# Create Mosquitto config
mkdir -p mosquitto/config
cat > mosquitto/config/mosquitto.conf << EOF
listener 1883
allow_anonymous true
listener 9001
protocol websockets
EOF

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Endpoints:"
echo "   • Frontend:    http://localhost:5173 (run 'cd frontend && npm run dev')"
echo "   • Backend API: http://localhost:8000"
echo "   • API Docs:    http://localhost:8000/docs"
echo "   • Ditto API:   http://localhost:8080"
echo ""
echo "🔧 To start the frontend:"
echo "   cd frontend && npm install && npm run dev"
echo ""
echo "📦 To start the demo simulator:"
echo "   cd demo && pip install -r requirements.txt && python simulator.py"
echo ""
