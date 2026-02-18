# Quick Start Guide

## Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.10+ (for AI layer and demo)

## 🚀 One-Command Start

```bash
chmod +x start.sh
./start.sh
```

## Manual Start

### 1. Backend + Ditto (Docker)

```bash
# Create Mosquitto config
mkdir -p mosquitto/config
cat > mosquitto/config/mosquitto.conf << EOF
listener 1883
allow_anonymous true
listener 9001
protocol websockets
EOF

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

### 3. Demo Simulator (optional)

```bash
cd demo
pip install -r requirements.txt
python simulator.py
```

## 📍 Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | React dashboard |
| Backend API | http://localhost:8000 | FastAPI REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Ditto API | http://localhost:8080 | Eclipse Ditto |
| MQTT | localhost:1883 | Mosquitto broker |

## 🧪 Test the API

```bash
# Health check
curl http://localhost:8000/health

# Create a digital twin
curl -X POST http://localhost:8000/things/ \
  -H "Content-Type: application/json" \
  -d '{
    "thing_id": "factory:machine-001",
    "attributes": {
      "name": "CNC Machine 1",
      "type": "machine",
      "location": "Factory A - Line 1"
    },
    "features": {
      "temperature": {
        "properties": {
          "value": 45.2,
          "unit": "°C"
        }
      }
    }
  }'

# List all twins
curl http://localhost:8000/things/

# Get a specific twin
curl http://localhost:8000/things/factory:machine-001
```

## 🧠 AI Features

The AI layer requires an OpenAI API key:

```bash
export OPENAI_API_KEY=your-key-here
```

Or add to `.env`:

```
OPENAI_API_KEY=your-key-here
```

### AI Examples

```python
from ai import predict_failure, detect_anomalies, generate_insights

# Predict equipment failure
result = predict_failure(sensor_history, equipment_type="machine")
print(f"Failure probability: {result.failure_probability:.1%}")

# Detect anomalies
anomalies = detect_anomalies(sensor_data)
for a in anomalies:
    print(f"[{a.severity.value}] {a.sensor_name}: {a.description}")

# Generate AI insights
insights = generate_insights(twin_data)
for i in insights:
    print(f"{i['title']}: {i['description']}")
```

## 📁 Project Structure

```
digital-twins-platform/
├── docker-compose.yml    # All services
├── backend/              # FastAPI backend
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # React + TypeScript
│   ├── src/
│   │   ├── pages/       # Dashboard, TwinList, etc.
│   │   ├── components/  # Reusable UI
│   │   └── services/    # API client
│   └── package.json
├── ai/                   # AI/ML layer
│   ├── predictor.py     # Failure prediction
│   ├── anomaly.py       # Anomaly detection
│   ├── simulator.py     # What-if simulation
│   └── llm_interface.py # Natural language
├── demo/                 # Demo data & simulator
│   ├── demo_twins.json  # Sample twins
│   └── simulator.py     # Sensor simulator
└── docs/
    └── PITCH.md         # Product pitch
```

## 🐛 Troubleshooting

### Docker services not starting

```bash
# Check logs
docker-compose logs

# Restart specific service
docker-compose restart gateway
```

### Frontend not connecting to backend

Check that backend is running:
```bash
curl http://localhost:8000/health
```

### Ditto health check failing

Wait longer - Ditto services take 60-90 seconds to fully start:
```bash
docker-compose logs gateway
```

## 📦 What's Included

- ✅ Eclipse Ditto (Digital Twin core)
- ✅ MongoDB (Ditto persistence)
- ✅ Mosquitto (MQTT broker)
- ✅ FastAPI Backend (REST + WebSocket)
- ✅ React Frontend (Dashboard + 3D viewer)
- ✅ AI Layer (Prediction + Anomaly + Simulation)
- ✅ Demo Data (10 industrial equipment twins)
