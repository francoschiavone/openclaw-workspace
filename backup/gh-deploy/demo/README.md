# Digital Twins Demo

Realistic demo data and simulation tools for the Digital Twins Platform. This package provides sample digital twins, data simulators, and scenario scripts to demonstrate the platform's capabilities.

## 📦 Contents

```
demo/
├── demo_twins.json          # Sample digital twins configuration
├── simulator.py             # Real-time data simulator
├── generate_history.py      # Historical data generator
├── scenario_normal.py       # Normal operation scenario
├── scenario_degradation.py  # Equipment degradation scenario
├── scenario_failure.py      # Imminent failure scenario
├── scenario_recovery.py     # Recovery after maintenance scenario
├── historical/              # Generated historical data (CSV files)
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

```bash
# Required
pip install requests

# Optional (for MQTT support)
pip install paho-mqtt
```

### Run a Demo Scenario

```bash
# 1. Generate historical data first
python generate_history.py

# 2. Run the normal operation scenario
python scenario_normal.py --duration 60

# 3. Try other scenarios
python scenario_degradation.py --duration 120
python scenario_failure.py --duration 90 --failure-time 30
python scenario_recovery.py --duration 150
```

## 📊 Sample Digital Twins

The `demo_twins.json` file contains **12 realistic digital twins**:

### Factory Machines
| ID | Name | Type | Description |
|----|------|------|-------------|
| twin-001 | CNC Milling Machine Alpha | machine/cnc_mill | 5-axis CNC mill with spindle and coolant subsystems |
| twin-002 | Robotic Arm Beta | machine/robotic_arm | 6-axis industrial robot for assembly |
| twin-003 | Conveyor Belt Gamma | machine/conveyor | Material handling conveyor system |

### HVAC Systems
| ID | Name | Type | Description |
|----|------|------|-------------|
| twin-004 | HVAC System North | hvac/central_air | Central air conditioning with compressor and fan |
| twin-005 | HVAC System South | hvac/central_air | Central air conditioning (warning status) |

### Utility Equipment
| ID | Name | Type | Description |
|----|------|------|-------------|
| twin-006 | Power Generator Prime | generator/diesel_generator | 500kW backup diesel generator |
| twin-007 | Water Pump Station | pump/centrifugal_pump | Industrial water circulation pump |

### Storage Tanks
| ID | Name | Type | Description |
|----|------|------|-------------|
| twin-008 | Storage Tank A - Raw Material | tank/chemical_tank | 50,000L raw material storage |
| twin-009 | Storage Tank B - Finished Product | tank/product_tank | 75,000L product storage |

### Twin Structure

Each twin includes:
```json
{
  "id": "twin-001",
  "name": "CNC Milling Machine Alpha",
  "type": "machine",
  "subtype": "cnc_mill",
  "location": {
    "building": "Factory-A",
    "floor": 1,
    "area": "Production Line 1",
    "coordinates": {"x": 12.5, "y": 8.3}
  },
  "sensors": [
    {
      "id": "s001-temp",
      "name": "Spindle Temperature",
      "unit": "°C",
      "min": 20,
      "max": 120,
      "current_value": 45.2,
      "warning_threshold": 80,
      "critical_threshold": 100
    }
  ],
  "status": "operational",
  "metadata": {
    "manufacturer": "Haas Automation",
    "model": "VF-2SS",
    "install_date": "2022-03-15",
    "last_maintenance": "2025-11-20"
  },
  "children": ["twin-001-spindle", "twin-001-coolant"],
  "parent": null
}
```

## 🎮 Data Simulator

The `simulator.py` script generates real-time sensor data:

### Usage

```bash
# Basic console output
python simulator.py --console

# With REST API publishing
python simulator.py --rest-url http://localhost:8000

# With MQTT publishing
python simulator.py --mqtt-broker localhost --mqtt-port 1883

# Specific twins only
python simulator.py --twins twin-001 twin-002 --console

# Run for specific duration
python simulator.py --duration 300 --console
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--config` | Path to twins config file | demo_twins.json |
| `--interval` | Update interval in seconds | 1.0 |
| `--duration` | Simulation duration (None = infinite) | None |
| `--scenario` | Simulation mode (normal/degradation/failure/recovery) | normal |
| `--rest-url` | REST API base URL | None |
| `--mqtt-broker` | MQTT broker address | None |
| `--mqtt-port` | MQTT broker port | 1883 |
| `--console` | Output to console | False |
| `--twins` | Specific twin IDs to simulate | All |
| `-v, --verbose` | Enable verbose logging | False |

### Sensor Simulation

The simulator creates realistic sensor behavior:
- **Temperature sensors**: Daily cycles, operating heat, noise
- **Vibration sensors**: Harmonic components, random spikes
- **Power sensors**: Load variations, efficiency changes
- **Flow sensors**: Pulsation, pressure effects
- **Level sensors**: Gradual changes, noise
- **Counter sensors**: Time-based accumulation

## 📈 Historical Data Generator

Generate synthetic historical data for analytics demos:

```bash
# Generate 30 days of hourly data
python generate_history.py

# Custom duration and output
python generate_history.py --days 60 --output my_history

# Specific start date
python generate_history.py --start-date 2025-01-01 --days 30
```

### Output

Generates CSV files in `historical/`:
```
historical/
├── twin-001_history.csv
├── twin-002_history.csv
├── ...
├── generation_summary.json
└── INCIDENTS.md
```

### Data Patterns

Historical data includes:
- **Daily cycles**: Activity varies by hour
- **Weekly patterns**: Reduced activity on weekends
- **Working hours**: Higher values during 8am-6pm
- **Random incidents**: Spikes, drops, drift events
- **Noise**: Realistic sensor noise

## 🎭 Scenario Scripts

### 1. Normal Operation (`scenario_normal.py`)

All equipment running normally.

```bash
python scenario_normal.py --duration 60
```

Use case: Baseline demo, platform health check

### 2. Equipment Degradation (`scenario_degradation.py`)

Gradual equipment degradation over time.

```bash
python scenario_degradation.py --duration 120
```

Use case: **Predictive maintenance** demonstration

What to watch:
- Increasing temperatures
- Rising vibration levels
- Status changes: OPERATIONAL → WARNING → CRITICAL

### 3. Imminent Failure (`scenario_failure.py`)

Equipment failure with warning signs.

```bash
python scenario_failure.py --duration 90 --failure-time 30 --failure-type cascade
```

Use case: **Emergency response** demonstration

Failure types:
- `gradual`: Slow failure progression
- `sudden`: Immediate failure
- `cascade`: Failure spreads to connected equipment

### 4. Recovery After Maintenance (`scenario_recovery.py`)

Equipment recovery after maintenance intervention.

```bash
python scenario_recovery.py --duration 150 --maintenance-time 30
```

Use case: **Maintenance effectiveness** tracking

Timeline:
1. 0-30s: Degraded operation
2. 30-60s: Maintenance in progress
3. 60-150s: Recovery to normal

## 🔌 Integration

### REST API Integration

The simulator can POST data to your backend:

```bash
python simulator.py --rest-url https://api.yourplatform.com
```

Expected endpoint: `POST /api/v1/twins/{twin_id}/telemetry`

Payload:
```json
{
  "twin_id": "twin-001",
  "name": "CNC Milling Machine Alpha",
  "type": "machine",
  "status": "operational",
  "timestamp": "2025-01-15T10:30:00Z",
  "sensors": [
    {
      "sensor_id": "s001-temp",
      "name": "Spindle Temperature",
      "unit": "°C",
      "value": 45.2,
      "min": 20,
      "max": 120,
      "warning_threshold": 80,
      "critical_threshold": 100
    }
  ]
}
```

### MQTT Integration

Publish to MQTT topics:

```bash
python simulator.py --mqtt-broker broker.hivemq.com
```

Topic format: `digitaltwins/{twin_id}/telemetry`

### Custom Integration

Use the simulator as a module:

```python
from simulator import SimulationController, SimulationMode, ConsolePublisher

controller = SimulationController('demo_twins.json')
controller.update_interval = 2.0  # 2 second updates
controller.set_mode(SimulationMode.NORMAL)
controller.add_publisher(ConsolePublisher())

# Run for 60 seconds
controller.run(duration=60)
```

## 📋 Demo Checklist

For a complete demo:

1. **Setup**
   ```bash
   cd demo
   python generate_history.py  # Generate 30 days of historical data
   ```

2. **Normal Operations** (2 min)
   ```bash
   python scenario_normal.py --duration 120
   ```
   Show: Dashboard, real-time charts, all green status

3. **Predictive Maintenance** (3 min)
   ```bash
   python scenario_degradation.py --duration 180
   ```
   Show: Trend analysis, warnings, predicted failures

4. **Emergency Response** (2 min)
   ```bash
   python scenario_failure.py --duration 120 --failure-time 30
   ```
   Show: Alerts, notifications, critical status

5. **Maintenance & Recovery** (3 min)
   ```bash
   python scenario_recovery.py --duration 180
   ```
   Show: Maintenance tracking, recovery metrics

6. **Historical Analytics**
   Show: Historical data visualizations, incident analysis

## 🔧 Troubleshooting

### "Module not found: paho"
```bash
pip install paho-mqtt
# Or run without MQTT
python simulator.py --console
```

### "Connection refused" (REST/MQTT)
Ensure your backend services are running:
```bash
# Check REST API
curl http://localhost:8000/health

# Check MQTT broker
mosquitto_pub -h localhost -t test -m "hello"
```

### No data showing
- Verify `demo_twins.json` exists
- Check console output for errors
- Use `--verbose` flag for detailed logging

## 📝 License

Demo data created for Digital Twins Platform demonstration purposes.

## 🤝 Contributing

To add new digital twins:
1. Edit `demo_twins.json`
2. Follow the existing structure
3. Run `python simulator.py --console` to test

---

**Questions?** Contact the Digital Twins Platform team.
