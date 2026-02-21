# Digital Twins Platform

A production-ready Digital Twins platform built on **Eclipse Ditto™** with a Python FastAPI backend.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Digital Twins Platform                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐     │
│  │   Frontend   │────▶│   FastAPI    │────▶│    Ditto     │     │
│  │   (Client)   │     │   Backend    │     │   Gateway    │     │
│  └──────────────┘     └──────────────┘     └──────────────┘     │
│                              │                   │               │
│                              │                   ▼               │
│                              │         ┌──────────────────┐     │
│                              │         │ Ditto Services   │     │
│                              │         │ • Policies       │     │
│                              │         │ • Things         │     │
│                              │         │ • Things-Search  │     │
│                              │         │ • Connectivity   │     │
│                              │         └──────────────────┘     │
│                              │                   │               │
│                              ▼                   ▼               │
│                       ┌──────────────┐   ┌──────────────┐       │
│                       │   Mosquitto  │   │   MongoDB    │       │
│                       │    MQTT      │   │  (Persist)   │       │
│                       └──────────────┘   └──────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### Eclipse Ditto Services
- **Gateway**: HTTP/WebSocket API entry point
- **Policies**: Access control and authorization
- **Things**: Digital twin state management
- **Things-Search**: Search and query capabilities
- **Connectivity**: External system integration (MQTT, AMQP, Kafka)

### Infrastructure
- **MongoDB 7.0**: Persistent storage for Ditto
- **Mosquitto 2.0**: MQTT broker for IoT device connectivity
- **FastAPI Backend**: Custom Python API layer

## Prerequisites

- Docker Engine 24.0+
- Docker Compose 2.20+
- 8GB+ RAM recommended
- 4 CPU cores recommended

## Quick Start

### 1. Clone and Start

```bash
# Navigate to the project directory
cd digital-twins-platform

# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 2. Wait for Services to Be Ready

```bash
# Wait for health checks to pass (about 1-2 minutes)
docker-compose logs -f gateway
```

You should see `Health check passed` messages when Ditto is ready.

### 3. Verify Installation

```bash
# Check Ditto health
curl http://localhost:8080/health

# Check backend health
curl http://localhost:8000/health
```

### 4. Access the APIs

- **FastAPI Backend**: http://localhost:8000 (Interactive docs: http://localhost:8000/docs)
- **Ditto Gateway**: http://localhost:8080 (API docs: http://localhost:8080/apidoc)
- **MQTT Broker**: localhost:1883

## API Usage Examples

### Create a Digital Twin

```bash
# Using the FastAPI backend
curl -X POST http://localhost:8000/things/ \
  -H "Content-Type: application/json" \
  -d '{
    "thing_id": "com.example:temperature-sensor-01",
    "attributes": {
      "type": "temperature-sensor",
      "location": "warehouse-1",
      "manufacturer": "Example Corp"
    },
    "features": {
      "temperature": {
        "properties": {
          "value": 22.5,
          "unit": "celsius"
        }
      }
    }
  }'
```

### Get a Digital Twin

```bash
curl http://localhost:8000/things/com.example:temperature-sensor-01
```

### Update a Feature

```bash
curl -X PUT http://localhost:8000/things/com.example:temperature-sensor-01/features/temperature \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "value": 24.0,
      "unit": "celsius"
    }
  }'
```

### Search Digital Twins

```bash
# Search by attribute
curl "http://localhost:8000/search/things?q=eq(attributes/location,%22warehouse-1%22)"

# Search by feature property
curl "http://localhost:8000/search/things?q=gt(features/temperature/properties/value,20)"
```

### Delete a Digital Twin

```bash
curl -X DELETE http://localhost:8000/things/com.example:temperature-sensor-01
```

## WebSocket Integration

### Real-time Events

Connect to receive live updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/events');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event received:', data);
};

ws.onopen = () => {
  console.log('Connected to event stream');
};
```

### Direct Ditto WebSocket

For advanced use cases, connect directly to Ditto:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/ditto');

ws.onopen = () => {
  // Subscribe to thing changes
  ws.send(JSON.stringify({
    "type": "subscribe",
    "filter": "like(thingId,'*')"
  }));
};
```

## MQTT Integration

### Publish Device Telemetry

```bash
# Install mosquitto clients
# apt-get install mosquitto-clients

# Publish temperature reading
mosquitto_pub -h localhost -p 1883 \
  -t "devices/com.example:temperature-sensor-01/telemetry" \
  -m '{"temperature": 25.5, "humidity": 60}'
```

### Subscribe to Device Commands

```bash
mosquitto_sub -h localhost -p 1883 \
  -t "devices/+/commands" \
  -v
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Ditto version
DITTO_VERSION=3.8.0

# MongoDB credentials
MONGO_INITDB_ROOT_USERNAME=ditto
MONGO_INITDB_ROOT_PASSWORD=your-secure-password

# DevOps credentials (change in production!)
DITTO_DEVOPS_USER=devops
DITTO_DEVOPS_PASSWORD=your-secure-password
```

### Backend Configuration

The FastAPI backend can be configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| DITTO_API_URL | http://gateway:8080 | Ditto Gateway URL |
| DITTO_WS_URL | ws://gateway:8081 | Ditto WebSocket URL |
| DITTO_DEVOPS_USER | devops | DevOps username |
| DITTO_DEVOPS_PASSWORD | dittoPwd | DevOps password |
| MQTT_BROKER_URL | mqtt://mosquitto:1883 | MQTT broker URL |
| LOG_LEVEL | INFO | Logging level |

## Development

### Local Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
DITTO_API_URL=http://localhost:8080 uvicorn main:app --reload
```

### Running Tests

```bash
cd backend
pytest -v --cov=.
```

### Building Backend Image

```bash
docker build -t digital-twins-backend ./backend
```

## Production Deployment

### Security Checklist

1. **Change all default passwords** in `.env`
2. **Enable TLS** for all services
3. **Configure authentication** for Ditto (OIDC, pre-auth)
4. **Set up MongoDB replica set** for high availability
5. **Configure Mosquitto authentication**
6. **Use secrets management** (Docker secrets, Vault, etc.)
7. **Enable network policies** in production

### High Availability

For production, consider:

1. **MongoDB Replica Set**: For data redundancy
2. **Multiple Ditto instances**: Scale with Docker Swarm or Kubernetes
3. **Load Balancer**: HAProxy or nginx for gateway
4. **Container Orchestration**: Kubernetes with Helm charts

### Resource Requirements

| Service | CPU | Memory | Storage |
|---------|-----|--------|---------|
| MongoDB | 1 core | 2 GB | 50 GB |
| Ditto Services | 2 cores | 4 GB total | - |
| Mosquitto | 0.5 core | 512 MB | 1 GB |
| Backend | 1 core | 512 MB | - |

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs -f

# Check specific service
docker-compose logs gateway

# Restart services
docker-compose restart
```

### MongoDB Connection Issues

```bash
# Check MongoDB is running
docker-compose ps mongodb

# Connect to MongoDB
docker-compose exec mongodb mongosh -u ditto -p ditto
```

### Ditto Health Check Failing

```bash
# Check gateway health directly
curl http://localhost:8080/health

# Check all Ditto services
docker-compose logs policies things things-search connectivity gateway
```

### Backend Can't Connect to Ditto

```bash
# Check network connectivity
docker-compose exec backend ping gateway

# Check environment variables
docker-compose exec backend env | grep DITTO
```

## Useful Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# View logs
docker-compose logs -f

# Scale backend
docker-compose up -d --scale backend=3

# Execute command in container
docker-compose exec backend /bin/bash

# Check resource usage
docker stats
```

## API Reference

### FastAPI Backend Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| POST | /things/ | Create a digital twin |
| GET | /things/ | List digital twins |
| GET | /things/{id} | Get a digital twin |
| PATCH | /things/{id} | Update a digital twin |
| DELETE | /things/{id} | Delete a digital twin |
| GET | /things/{id}/features/{fid} | Get a feature |
| PUT | /things/{id}/features/{fid} | Update a feature |
| POST | /policies/ | Create a policy |
| GET | /policies/{id} | Get a policy |
| DELETE | /policies/{id} | Delete a policy |
| GET | /search/things | Search things |
| WS | /ws/events | Real-time events |
| WS | /ws/ditto | Ditto WebSocket proxy |

## Project Structure

```
digital-twins-platform/
├── docker-compose.yml      # Main compose file
├── .env                    # Environment variables
├── README.md               # This file
├── ditto/
│   └── README.md          # Ditto configuration docs
├── mosquitto/
│   └── config/
│       └── mosquitto.conf # MQTT broker config
└── backend/
    ├── Dockerfile         # Backend container
    ├── requirements.txt   # Python dependencies
    ├── main.py           # FastAPI application
    ├── config.py         # Configuration
    ├── models.py         # Pydantic models
    └── .env.example      # Example environment
```

## License

This project is provided as-is. Eclipse Ditto is licensed under the Eclipse Public License 2.0.

## Resources

- [Eclipse Ditto Documentation](https://eclipse.dev/ditto/)
- [Eclipse Ditto HTTP API](https://eclipse.dev/ditto/httpapi-overview.html)
- [Eclipse Ditto Protocol](https://eclipse.dev/ditto/protocol-overview.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Mosquitto Documentation](https://mosquitto.org/documentation/)
