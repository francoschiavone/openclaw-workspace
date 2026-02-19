# AI/ML Layer for Digital Twins Platform

This module provides predictive analytics, anomaly detection, simulation capabilities, and LLM-powered natural language interfaces for digital twin operations.

## Installation

```bash
pip install -r requirements.txt
```

## Module Structure

```
ai/
├── __init__.py           # Package exports
├── requirements.txt      # Python dependencies
├── predictor.py          # ML models for prediction
├── anomaly.py            # Anomaly detection
├── simulator.py          # What-if simulation engine
├── llm_interface.py      # LLM integration for natural language
├── api_integration.py    # FastAPI integration
├── README.md             # This file
└── models/
    ├── __init__.py
    └── pretrained/       # Saved models directory
```

## Quick Start

### Prediction Module

```python
from ai.predictor import predict_failure, predict_maintenance, forecast_metric

# Predict equipment failure
sensor_history = [
    {"timestamp": "2024-01-01T10:00:00", "value": 45.2},
    {"timestamp": "2024-01-01T10:05:00", "value": 46.1},
    # ... more readings
]
result = predict_failure(sensor_history)
print(f"Failure probability: {result['probability']:.1%}")

# Predict maintenance needs
equipment_data = {
    "operating_hours": 5000,
    "last_maintenance": "2023-06-15",
    "maintenance_history": [...],
    "sensor_data": [...]
}
maintenance = predict_maintenance(equipment_data)
print(f"Maintenance urgency: {maintenance['urgency']}")

# Forecast metrics
forecast = forecast_metric(metric_history, horizon=24)
for point in forecast:
    print(f"{point['timestamp']}: {point['value']:.2f}")
```

### Anomaly Detection

```python
from ai.anomaly import detect_anomalies, get_anomaly_score

# Detect anomalies in sensor data
anomalies = detect_anomalies(
    sensor_data,
    sensitivity=0.7  # Higher = more sensitive
)
for anomaly in anomalies:
    print(f"Anomaly at {anomaly['timestamp']}: {anomaly['description']}")

# Get anomaly score for a single value
baseline = {"mean": 50, "std": 10}
score = get_anomaly_score(85, baseline)
print(f"Anomaly score: {score:.2f}")
```

### Simulation

```python
from ai.simulator import simulate_scenario, generate_scenarios

# Run a what-if scenario
twin_state = {
    "twin_id": "pump-001",
    "metrics": {"flow_rate": 100, "temperature": 45},
    "components": {"motor": {"health": 0.9, "status": "running"}}
}

scenario = {
    "name": "High Load Test",
    "type": "stress_test",
    "parameters": {"stress_factor": 1.5},
    "duration_hours": 24
}

result = simulate_scenario(twin_state, scenario)
print(f"Simulation confidence: {result['confidence']:.1%}")

# Generate relevant scenarios
scenarios = generate_scenarios(twin_state)
for s in scenarios:
    print(f"{s['name']}: {s['description']}")
```

### LLM Interface

```python
from ai.llm_interface import query_twin, generate_insights, explain_anomaly

# Ask a question about a twin
answer = query_twin(
    "What is the current health status of the motor?",
    twin_data
)
print(answer)

# Generate AI insights
insights = generate_insights(twin_data)
for insight in insights:
    print(f"[{insight['severity']}] {insight['title']}: {insight['description']}")

# Explain an anomaly
explanation = explain_anomaly(
    anomaly={"value": 150, "score": 0.85, "severity": "high"},
    context={"baseline": {"mean": 50, "std": 10}}
)
print(explanation)
```

## FastAPI Integration

```python
from fastapi import FastAPI
from ai.api_integration import ai_router

app = FastAPI()
app.include_router(ai_router, prefix="/api/ai", tags=["AI/ML"])
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai/predict/failure` | POST | Predict equipment failure |
| `/api/ai/predict/maintenance` | POST | Predict maintenance needs |
| `/api/ai/predict/forecast` | POST | Forecast metrics |
| `/api/ai/anomalies/detect` | POST | Detect anomalies |
| `/api/ai/anomalies/score` | POST | Get anomaly score |
| `/api/ai/simulate` | POST | Run scenario simulation |
| `/api/ai/simulate/generate-scenarios` | POST | Generate scenarios |
| `/api/ai/llm/query` | POST | Natural language query |
| `/api/ai/llm/insights` | POST | Generate insights |
| `/api/ai/llm/explain-anomaly` | POST | Explain anomaly |
| `/api/ai/health` | GET | Health check |

## Configuration

### LLM Configuration

Set environment variables for LLM integration:

```bash
# For OpenAI
export OPENAI_API_KEY="your-api-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-api-key"
```

Or configure programmatically:

```python
from ai.llm_interface import LLMInterface, LLMConfig

config = LLMConfig(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",
    temperature=0.5
)
interface = LLMInterface(config)
```

## Error Handling

All modules define specific exception types:

- `PredictionError` - Base for prediction errors
- `InsufficientDataError` - Not enough data for analysis
- `InvalidInputError` - Invalid input format
- `AnomalyError` - Base for anomaly detection errors
- `SimulationError` - Base for simulation errors
- `LLMError` - Base for LLM errors

Example:

```python
from ai.predictor import predict_failure, PredictionError, InsufficientDataError

try:
    result = predict_failure(sensor_history)
except InsufficientDataError as e:
    print(f"Need more data: {e}")
except PredictionError as e:
    print(f"Prediction failed: {e}")
```

## Production Considerations

1. **Caching**: Consider caching prediction results for frequently queried twins
2. **Rate Limiting**: Implement rate limiting for LLM endpoints
3. **Async Processing**: Use background tasks for long-running simulations
4. **Model Versioning**: Store model versions in `models/pretrained/`
5. **Monitoring**: Log prediction confidence and accuracy metrics

## Testing

```bash
# Run tests (when available)
pytest tests/

# Test imports
python -c "from ai import predict_failure, detect_anomalies, simulate_scenario, query_twin"
```

## License

MIT License - See LICENSE file for details.
