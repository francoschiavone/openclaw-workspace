#!/usr/bin/env python3
"""
Digital Twins Data Simulator

Simulates realistic sensor data updates for digital twins and publishes
via REST API and/or MQTT.

Usage:
    python simulator.py [--config config.json] [--scenario normal|degradation|failure|recovery]
"""

import json
import time
import random
import math
import argparse
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import threading
import requests
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DigitalTwinsSimulator')


class TwinStatus(Enum):
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"
    WARNING = "warning"
    CRITICAL = "critical"


class SimulationMode(Enum):
    NORMAL = "normal"
    DEGRADATION = "degradation"
    FAILURE = "failure"
    RECOVERY = "recovery"


@dataclass
class SensorReading:
    """Represents a single sensor reading"""
    sensor_id: str
    name: str
    unit: str
    value: float
    min_value: float
    max_value: float
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "sensor_id": self.sensor_id,
            "name": self.name,
            "unit": self.unit,
            "value": round(self.value, 3),
            "min": self.min_value,
            "max": self.max_value,
            "warning_threshold": self.warning_threshold,
            "critical_threshold": self.critical_threshold,
            "timestamp": self.timestamp
        }


class SensorSimulator(ABC):
    """Abstract base class for sensor simulation"""
    
    def __init__(self, sensor_config: Dict, mode: SimulationMode = SimulationMode.NORMAL):
        self.config = sensor_config
        self.mode = mode
        self.base_value = sensor_config['current_value']
        self.current_value = self.base_value
        self.min_val = sensor_config['min']
        self.max_val = sensor_config['max']
        self.warning_threshold = sensor_config.get('warning_threshold')
        self.critical_threshold = sensor_config.get('critical_threshold')
        self.degradation_factor = 0.0
        self.time_offset = random.uniform(0, 2 * math.pi)
        
    @abstractmethod
    def generate_value(self, elapsed_time: float) -> float:
        pass
    
    def update(self, elapsed_time: float) -> SensorReading:
        self.current_value = self.generate_value(elapsed_time)
        self.current_value = max(self.min_val, min(self.max_val, self.current_value))
        
        return SensorReading(
            sensor_id=self.config['id'],
            name=self.config['name'],
            unit=self.config['unit'],
            value=self.current_value,
            min_value=self.min_val,
            max_value=self.max_val,
            warning_threshold=self.warning_threshold,
            critical_threshold=self.critical_threshold
        )
    
    def set_degradation(self, factor: float):
        """Set degradation factor (0.0 = no degradation, 1.0 = severe)"""
        self.degradation_factor = max(0.0, min(1.0, factor))


class TemperatureSensor(SensorSimulator):
    """Simulates temperature sensors with realistic patterns"""
    
    def generate_value(self, elapsed_time: float) -> float:
        # Base temperature with daily cycle
        daily_cycle = 3 * math.sin((elapsed_time / 86400) * 2 * math.pi + self.time_offset)
        
        # Operating heat generation
        operating_heat = 15 * (0.7 + 0.3 * math.sin(elapsed_time / 300))
        
        # Random noise
        noise = random.gauss(0, 1.5)
        
        # Degradation causes temperature increase
        degradation_effect = self.degradation_factor * 30
        
        value = self.base_value + daily_cycle + operating_heat + noise + degradation_effect
        
        # Add occasional anomalies
        if random.random() < 0.001:
            value += random.gauss(10, 5)
            
        return value


class VibrationSensor(SensorSimulator):
    """Simulates vibration sensors"""
    
    def generate_value(self, elapsed_time: float) -> float:
        # Base vibration
        base = self.base_value
        
        # Harmonic components
        harmonic1 = 0.3 * math.sin(elapsed_time * 10 + self.time_offset)
        harmonic2 = 0.2 * math.sin(elapsed_time * 25)
        
        # Random noise
        noise = random.gauss(0, 0.2)
        
        # Degradation causes increased vibration
        degradation_effect = self.degradation_factor * 15
        
        value = base + harmonic1 + harmonic2 + noise + degradation_effect
        
        # Occasional vibration spikes
        if random.random() < 0.005:
            value += random.gauss(5, 2)
            
        return max(0, value)


class RPMSensor(SensorSimulator):
    """Simulates RPM/speed sensors"""
    
    def generate_value(self, elapsed_time: float) -> float:
        # Slight variation around base value
        variation = 50 * math.sin(elapsed_time / 60 + self.time_offset)
        noise = random.gauss(0, 20)
        
        # Degradation causes speed fluctuation
        degradation_effect = self.degradation_factor * random.gauss(0, 100)
        
        return self.base_value + variation + noise + degradation_effect


class PowerSensor(SensorSimulator):
    """Simulates power consumption sensors"""
    
    def generate_value(self, elapsed_time: float) -> float:
        # Load variation throughout the day
        hourly_pattern = 0.2 * math.sin((elapsed_time / 3600) * math.pi)
        
        # Short-term fluctuation
        fluctuation = 2 * math.sin(elapsed_time / 120 + self.time_offset)
        
        noise = random.gauss(0, 1)
        
        # Degradation increases power consumption
        degradation_effect = self.degradation_factor * 10
        
        value = self.base_value * (1 + hourly_pattern) + fluctuation + noise + degradation_effect
        
        return max(0, value)


class FlowSensor(SensorSimulator):
    """Simulates flow rate sensors"""
    
    def generate_value(self, elapsed_time: float) -> float:
        # Flow pulsation
        pulsation = 5 * math.sin(elapsed_time / 10 + self.time_offset)
        
        noise = random.gauss(0, 2)
        
        # Degradation reduces flow
        degradation_effect = -self.degradation_factor * 50
        
        value = self.base_value + pulsation + noise + degradation_effect
        
        return max(0, value)


class LevelSensor(SensorSimulator):
    """Simulates tank level sensors"""
    
    def __init__(self, sensor_config: Dict, mode: SimulationMode = SimulationMode.NORMAL):
        super().__init__(sensor_config, mode)
        self.drain_rate = random.uniform(-0.01, 0.02)  # Slight changes
        
    def generate_value(self, elapsed_time: float) -> float:
        # Gradual level change
        level_change = self.drain_rate * (elapsed_time / 60)
        
        noise = random.gauss(0, 0.5)
        
        value = self.current_value + level_change + noise
        
        # Wrap around for demo
        if value < self.min_val:
            value = self.max_val * 0.9
        elif value > self.max_val:
            value = self.min_val * 1.1
            
        return value


class PressureSensor(SensorSimulator):
    """Simulates pressure sensors"""
    
    def generate_value(self, elapsed_time: float) -> float:
        # Pressure fluctuations
        fluctuation = 0.5 * math.sin(elapsed_time / 30 + self.time_offset)
        noise = random.gauss(0, 0.2)
        
        # Degradation causes pressure issues
        degradation_effect = self.degradation_factor * 2
        
        return self.base_value + fluctuation + noise + degradation_effect


class CounterSensor(SensorSimulator):
    """Simulates counter/accumulating sensors (cycles, hours, etc.)"""
    
    def generate_value(self, elapsed_time: float) -> float:
        # Increment based on time
        increment = elapsed_time / 3600  # 1 hour per simulated hour
        
        # Add some randomness
        noise = random.gauss(0, 0.1)
        
        return self.current_value + increment + noise


class HumiditySensor(SensorSimulator):
    """Simulates humidity sensors"""
    
    def generate_value(self, elapsed_time: float) -> float:
        # Daily humidity cycle
        daily_cycle = 10 * math.sin((elapsed_time / 86400) * 2 * math.pi + self.time_offset)
        
        noise = random.gauss(0, 2)
        
        value = self.base_value + daily_cycle + noise
        
        return max(0, min(100, value))


class PercentageSensor(SensorSimulator):
    """Simulates percentage-based sensors (filter status, load, etc.)"""
    
    def __init__(self, sensor_config: Dict, mode: SimulationMode = SimulationMode.NORMAL):
        super().__init__(sensor_config, mode)
        self.direction = -1 if 'filter' in sensor_config['name'].lower() else 0
        
    def generate_value(self, elapsed_time: float) -> float:
        # Slow change in one direction for filters
        slow_change = self.direction * 0.001 * (elapsed_time / 60)
        
        # Small fluctuations
        fluctuation = 2 * math.sin(elapsed_time / 300 + self.time_offset)
        noise = random.gauss(0, 0.5)
        
        value = self.base_value + slow_change + fluctuation + noise
        
        return max(0, min(100, value))


def create_sensor_simulator(sensor_config: Dict, mode: SimulationMode) -> SensorSimulator:
    """Factory function to create appropriate sensor simulator"""
    name_lower = sensor_config['name'].lower()
    unit = sensor_config['unit'].lower()
    
    if 'temp' in name_lower or unit in ['°c', '°f']:
        return TemperatureSensor(sensor_config, mode)
    elif 'vib' in name_lower:
        return VibrationSensor(sensor_config, mode)
    elif 'rpm' in name_lower or 'speed' in name_lower:
        return RPMSensor(sensor_config, mode)
    elif 'power' in name_lower:
        return PowerSensor(sensor_config, mode)
    elif 'flow' in name_lower:
        return FlowSensor(sensor_config, mode)
    elif 'level' in name_lower:
        return LevelSensor(sensor_config, mode)
    elif 'pressure' in name_lower:
        return PressureSensor(sensor_config, mode)
    elif 'hour' in name_lower or 'cycl' in name_lower:
        return CounterSensor(sensor_config, mode)
    elif 'humid' in name_lower or unit == '%rh':
        return HumiditySensor(sensor_config, mode)
    elif unit == '%':
        return PercentageSensor(sensor_config, mode)
    else:
        # Default to basic sensor
        return PercentageSensor(sensor_config, mode)


class DigitalTwinSimulator:
    """Main simulator for a digital twin"""
    
    def __init__(self, twin_config: Dict, mode: SimulationMode = SimulationMode.NORMAL):
        self.config = twin_config
        self.id = twin_config['id']
        self.name = twin_config['name']
        self.type = twin_config['type']
        self.mode = mode
        self.status = twin_config['status']
        self.sensor_simulators: Dict[str, SensorSimulator] = {}
        self.degradation_start_time: Optional[float] = None
        self.degradation_duration = 3600  # 1 hour to full degradation
        
        # Initialize sensor simulators
        for sensor in twin_config['sensors']:
            self.sensor_simulators[sensor['id']] = create_sensor_simulator(sensor, mode)
    
    def update(self, elapsed_time: float) -> Dict[str, Any]:
        """Update all sensors and return readings"""
        sensor_readings = []
        
        # Calculate degradation if in degradation mode
        degradation_factor = 0.0
        if self.mode == SimulationMode.DEGRADATION:
            if self.degradation_start_time is None:
                self.degradation_start_time = elapsed_time
            degradation_elapsed = elapsed_time - self.degradation_start_time
            degradation_factor = min(1.0, degradation_elapsed / self.degradation_duration)
        elif self.mode == SimulationMode.FAILURE:
            degradation_factor = 0.8 + 0.2 * random.random()
        elif self.mode == SimulationMode.RECOVERY:
            if self.degradation_start_time is None:
                self.degradation_start_time = elapsed_time
            recovery_elapsed = elapsed_time - self.degradation_start_time
            degradation_factor = max(0.0, 1.0 - (recovery_elapsed / self.degradation_duration))
        
        for sensor_id, simulator in self.sensor_simulators.items():
            simulator.set_degradation(degradation_factor)
            reading = simulator.update(elapsed_time)
            sensor_readings.append(reading.to_dict())
        
        # Update status based on readings
        self._update_status(sensor_readings)
        
        return {
            "twin_id": self.id,
            "name": self.name,
            "type": self.type,
            "status": self.status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sensors": sensor_readings
        }
    
    def _update_status(self, readings: List[Dict]):
        """Update twin status based on sensor readings"""
        has_critical = False
        has_warning = False
        
        for reading in readings:
            value = reading['value']
            if reading.get('critical_threshold'):
                if (reading['critical_threshold'] > reading['min'] and 
                    value >= reading['critical_threshold']):
                    has_critical = True
                elif (reading['critical_threshold'] < reading['max'] and
                      value <= reading['critical_threshold']):
                    has_critical = True
            if reading.get('warning_threshold'):
                if (reading['warning_threshold'] > reading['min'] and
                    value >= reading['warning_threshold']):
                    has_warning = True
                elif (reading['warning_threshold'] < reading['max'] and
                      value <= reading['warning_threshold']):
                    has_warning = True
        
        if has_critical:
            self.status = TwinStatus.CRITICAL.value
        elif has_warning:
            self.status = TwinStatus.WARNING.value
        elif self.mode == SimulationMode.RECOVERY:
            self.status = TwinStatus.MAINTENANCE.value
        else:
            self.status = TwinStatus.OPERATIONAL.value
    
    def set_mode(self, mode: SimulationMode):
        """Change simulation mode"""
        self.mode = mode
        self.degradation_start_time = None
        logger.info(f"Twin {self.name} mode changed to {mode.value}")


class Publisher(ABC):
    """Abstract base class for data publishers"""
    
    @abstractmethod
    def publish(self, twin_data: Dict) -> bool:
        pass
    
    @abstractmethod
    def close(self):
        pass


class RESTPublisher(Publisher):
    """Publishes data to REST API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def publish(self, twin_data: Dict) -> bool:
        try:
            url = f"{self.base_url}/api/v1/twins/{twin_data['twin_id']}/telemetry"
            response = self.session.post(url, json=twin_data, timeout=5)
            
            if response.status_code == 200:
                logger.debug(f"Published to REST: {twin_data['twin_id']}")
                return True
            else:
                logger.warning(f"REST publish failed: {response.status_code}")
                return False
        except requests.RequestException as e:
            logger.error(f"REST publish error: {e}")
            return False
    
    def close(self):
        self.session.close()


class MQTTPublisher(Publisher):
    """Publishes data via MQTT"""
    
    def __init__(self, broker: str = "localhost", port: int = 1883,
                 username: str = None, password: str = None):
        self.broker = broker
        self.port = port
        self.client = None
        
        try:
            import paho.mqtt.client as mqtt
            self.client = mqtt.Client(client_id=f"simulator-{random.randint(1000, 9999)}")
            
            if username and password:
                self.client.username_pw_set(username, password)
            
            self.client.connect(broker, port, 60)
            self.client.loop_start()
            logger.info(f"Connected to MQTT broker at {broker}:{port}")
        except ImportError:
            logger.warning("paho-mqtt not installed. MQTT publishing disabled.")
            self.client = None
        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")
            self.client = None
    
    def publish(self, twin_data: Dict) -> bool:
        if not self.client:
            return False
        
        try:
            topic = f"digitaltwins/{twin_data['twin_id']}/telemetry"
            payload = json.dumps(twin_data)
            result = self.client.publish(topic, payload, qos=1)
            
            if result.rc == 0:
                logger.debug(f"Published to MQTT: {topic}")
                return True
            else:
                logger.warning(f"MQTT publish failed with code: {result.rc}")
                return False
        except Exception as e:
            logger.error(f"MQTT publish error: {e}")
            return False
    
    def close(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()


class ConsolePublisher(Publisher):
    """Publishes data to console (for testing)"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
    
    def publish(self, twin_data: Dict) -> bool:
        if self.verbose:
            print(f"\n[{twin_data['timestamp']}] {twin_data['name']} ({twin_data['status']})")
            for sensor in twin_data['sensors']:
                status = ""
                if sensor.get('critical_threshold'):
                    if sensor['value'] >= sensor['critical_threshold']:
                        status = " [CRITICAL]"
                    elif sensor.get('warning_threshold') and sensor['value'] >= sensor['warning_threshold']:
                        status = " [WARNING]"
                print(f"  {sensor['name']}: {sensor['value']:.2f} {sensor['unit']}{status}")
        return True
    
    def close(self):
        pass


class SimulationController:
    """Main controller for the simulation"""
    
    def __init__(self, config_path: str = "demo_twins.json"):
        self.config_path = config_path
        self.twins: Dict[str, DigitalTwinSimulator] = {}
        self.publishers: List[Publisher] = []
        self.running = False
        self.start_time: Optional[float] = None
        self.update_interval = 1.0  # seconds
        
        self._load_config()
    
    def _load_config(self):
        """Load twin configurations"""
        with open(self.config_path, 'r') as f:
            data = json.load(f)
        
        for twin_config in data['twins']:
            twin = DigitalTwinSimulator(twin_config)
            self.twins[twin.id] = twin
        
        logger.info(f"Loaded {len(self.twins)} digital twins")
    
    def add_publisher(self, publisher: Publisher):
        """Add a data publisher"""
        self.publishers.append(publisher)
    
    def set_mode(self, mode: SimulationMode, twin_ids: List[str] = None):
        """Set simulation mode for specific twins or all"""
        targets = twin_ids if twin_ids else list(self.twins.keys())
        for twin_id in targets:
            if twin_id in self.twins:
                self.twins[twin_id].set_mode(mode)
    
    def run(self, duration: float = None):
        """Run the simulation"""
        self.running = True
        self.start_time = time.time()
        
        logger.info(f"Starting simulation with {len(self.twins)} twins")
        logger.info(f"Update interval: {self.update_interval}s")
        logger.info(f"Publishers: {len(self.publishers)}")
        
        try:
            iteration = 0
            while self.running:
                elapsed_time = time.time() - self.start_time
                
                # Check duration
                if duration and elapsed_time >= duration:
                    logger.info(f"Simulation completed after {duration} seconds")
                    break
                
                # Update all twins
                for twin_id, twin in self.twins.items():
                    data = twin.update(elapsed_time)
                    
                    # Publish to all publishers
                    for publisher in self.publishers:
                        publisher.publish(data)
                
                iteration += 1
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the simulation"""
        self.running = False
        for publisher in self.publishers:
            publisher.close()
        logger.info("Simulation stopped")


def main():
    parser = argparse.ArgumentParser(description="Digital Twins Data Simulator")
    parser.add_argument('--config', default='demo_twins.json',
                       help='Path to twins configuration file')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Update interval in seconds')
    parser.add_argument('--duration', type=float, default=None,
                       help='Simulation duration in seconds (None = infinite)')
    parser.add_argument('--scenario', choices=['normal', 'degradation', 'failure', 'recovery'],
                       default='normal', help='Simulation scenario')
    parser.add_argument('--rest-url', default=None,
                       help='REST API base URL')
    parser.add_argument('--mqtt-broker', default=None,
                       help='MQTT broker address')
    parser.add_argument('--mqtt-port', type=int, default=1883,
                       help='MQTT broker port')
    parser.add_argument('--console', action='store_true',
                       help='Output to console')
    parser.add_argument('--twins', nargs='+', default=None,
                       help='Specific twin IDs to simulate')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create controller
    controller = SimulationController(args.config)
    controller.update_interval = args.interval
    
    # Filter twins if specified
    if args.twins:
        controller.twins = {k: v for k, v in controller.twins.items() if k in args.twins}
        logger.info(f"Simulating {len(controller.twins)} specific twins")
    
    # Set simulation mode
    mode = SimulationMode(args.scenario)
    controller.set_mode(mode)
    
    # Add publishers
    if args.console or (not args.rest_url and not args.mqtt_broker):
        controller.add_publisher(ConsolePublisher(verbose=True))
    
    if args.rest_url:
        controller.add_publisher(RESTPublisher(base_url=args.rest_url))
        logger.info(f"REST publisher configured: {args.rest_url}")
    
    if args.mqtt_broker:
        controller.add_publisher(MQTTPublisher(broker=args.mqtt_broker, port=args.mqtt_port))
        logger.info(f"MQTT publisher configured: {args.mqtt_broker}:{args.mqtt_port}")
    
    # Run simulation
    controller.run(duration=args.duration)


if __name__ == "__main__":
    main()
