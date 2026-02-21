#!/usr/bin/env python3
"""
Historical Data Generator for Digital Twins

Generates synthetic historical data for digital twins including:
- 30 days of hourly sensor readings
- Realistic daily and weekly patterns
- Simulated incidents (spikes, drops, failures)

Output: CSV files in demo/historical/
"""

import json
import csv
import os
import random
import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('HistoryGenerator')


@dataclass
class Incident:
    """Represents a simulated incident"""
    day: int  # Day number (0-29)
    hour: int  # Hour of day (0-23)
    duration_hours: int
    severity: str  # 'minor', 'major', 'critical'
    affected_sensors: List[str]
    type: str  # 'spike', 'drop', 'noise', 'drift'
    magnitude: float  # Multiplier for the effect


class HistoricalDataGenerator:
    """Generates historical data for a single sensor"""
    
    def __init__(self, sensor_config: Dict, days: int = 30):
        self.config = sensor_config
        self.days = days
        self.sensor_id = sensor_config['id']
        self.name = sensor_config['name']
        self.unit = sensor_config['unit']
        self.base_value = sensor_config['current_value']
        self.min_val = sensor_config['min']
        self.max_val = sensor_config['max']
        self.warning_threshold = sensor_config.get('warning_threshold')
        self.critical_threshold = sensor_config.get('critical_threshold')
        self.incidents: List[Incident] = []
        
    def add_incident(self, incident: Incident):
        """Add an incident to be simulated"""
        self.incidents.append(incident)
    
    def _get_incident_effect(self, hour_index: int) -> Tuple[float, str]:
        """Get the effect of any active incident at this hour"""
        day = hour_index // 24
        hour = hour_index % 24
        
        effect = 0.0
        status = 'normal'
        
        for incident in self.incidents:
            incident_hour = incident.day * 24 + incident.hour
            end_hour = incident_hour + incident.duration_hours
            
            if incident_hour <= hour_index < end_hour:
                # Check if this sensor is affected
                if self.sensor_id in incident.affected_sensors or '*' in incident.affected_sensors:
                    progress = (hour_index - incident_hour) / incident.duration_hours
                    
                    if incident.type == 'spike':
                        # Spike peaks in the middle
                        spike_factor = math.sin(progress * math.pi) * incident.magnitude
                        effect += spike_factor * (self.max_val - self.min_val) * 0.1
                    elif incident.type == 'drop':
                        # Drop is deepest in the middle
                        drop_factor = math.sin(progress * math.pi) * incident.magnitude
                        effect -= drop_factor * (self.base_value - self.min_val) * 0.3
                    elif incident.type == 'noise':
                        # Increased noise
                        effect += random.gauss(0, incident.magnitude * (self.max_val - self.min_val) * 0.05)
                    elif incident.type == 'drift':
                        # Gradual drift
                        effect += progress * incident.magnitude * (self.max_val - self.min_val) * 0.1
                    
                    if incident.severity == 'critical':
                        status = 'critical'
                    elif incident.severity == 'major' and status != 'critical':
                        status = 'warning'
                    elif status == 'normal':
                        status = 'warning'
        
        return effect, status
    
    def _apply_pattern(self, hour_index: int, base: float) -> float:
        """Apply daily and weekly patterns"""
        day_of_week = (hour_index // 24) % 7
        hour_of_day = hour_index % 24
        
        # Daily pattern (0-23 mapped to sinusoidal)
        daily_factor = math.sin((hour_of_day - 6) * math.pi / 12)
        
        # Weekly pattern (weekends have lower activity)
        weekly_factor = 0.8 if day_of_week >= 5 else 1.0
        
        # Working hours have higher activity (8am-6pm)
        working_hours = 0.3 if 8 <= hour_of_day < 18 else 0.0
        
        # Apply patterns based on sensor type
        name_lower = self.name.lower()
        
        if 'temp' in name_lower:
            # Temperature rises during working hours
            value = base + daily_factor * 10 + working_hours * 15
        elif 'power' in name_lower:
            # Power consumption follows activity
            value = base * weekly_factor * (0.6 + 0.4 * (0.5 + 0.5 * daily_factor))
        elif 'flow' in name_lower or 'level' in name_lower:
            # Flow/level varies with production
            value = base * (0.7 + 0.3 * weekly_factor * (0.5 + 0.5 * daily_factor))
        elif 'rpm' in name_lower or 'speed' in name_lower:
            # Speed follows production schedule
            if 8 <= hour_of_day < 18 and day_of_week < 5:
                value = base * (0.9 + 0.1 * random.random())
            else:
                value = base * 0.3 if random.random() > 0.3 else 0
        else:
            # Default pattern
            value = base * (0.8 + 0.2 * daily_factor)
        
        return value
    
    def generate(self, start_date: datetime) -> List[Dict]:
        """Generate historical data for the sensor"""
        data = []
        total_hours = self.days * 24
        
        for hour in range(total_hours):
            timestamp = start_date + timedelta(hours=hour)
            
            # Get base value with pattern
            value = self._apply_pattern(hour, self.base_value)
            
            # Add random noise
            noise = random.gauss(0, (self.max_val - self.min_val) * 0.02)
            value += noise
            
            # Apply incident effects
            incident_effect, status = self._get_incident_effect(hour)
            value += incident_effect
            
            # Clamp to valid range
            value = max(self.min_val, min(self.max_val, value))
            
            # Determine status if not affected by incident
            if status == 'normal':
                if self.critical_threshold:
                    if (self.critical_threshold > self.base_value and value >= self.critical_threshold):
                        status = 'critical'
                    elif (self.critical_threshold < self.base_value and value <= self.critical_threshold):
                        status = 'critical'
                if status == 'normal' and self.warning_threshold:
                    if (self.warning_threshold > self.base_value and value >= self.warning_threshold):
                        status = 'warning'
                    elif (self.warning_threshold < self.base_value and value <= self.warning_threshold):
                        status = 'warning'
            
            data.append({
                'timestamp': timestamp.isoformat(),
                'sensor_id': self.sensor_id,
                'sensor_name': self.name,
                'unit': self.unit,
                'value': round(value, 4),
                'status': status
            })
        
        return data


class TwinHistoryGenerator:
    """Generates historical data for a complete digital twin"""
    
    def __init__(self, twin_config: Dict, days: int = 30):
        self.config = twin_config
        self.twin_id = twin_config['id']
        self.twin_name = twin_config['name']
        self.twin_type = twin_config['type']
        self.days = days
        self.sensor_generators: Dict[str, HistoricalDataGenerator] = {}
        
        # Create generator for each sensor
        for sensor in twin_config['sensors']:
            self.sensor_generators[sensor['id']] = HistoricalDataGenerator(sensor, days)
    
    def generate_incidents(self):
        """Generate random incidents for this twin"""
        incidents_to_add = []
        
        # Probability of incidents based on twin type
        incident_probability = {
            'machine': 0.7,  # Machines have more issues
            'hvac': 0.5,
            'generator': 0.3,
            'pump': 0.4,
            'tank': 0.2
        }.get(self.twin_type, 0.3)
        
        # Generate 0-3 incidents
        num_incidents = random.choices([0, 1, 2, 3], 
                                        weights=[1-incident_probability, 
                                                incident_probability*0.5, 
                                                incident_probability*0.3,
                                                incident_probability*0.1])[0]
        
        for _ in range(num_incidents):
            day = random.randint(0, self.days - 3)
            hour = random.randint(8, 16)  # Incidents during working hours
            
            incident = Incident(
                day=day,
                hour=hour,
                duration_hours=random.randint(1, 8),
                severity=random.choices(['minor', 'major', 'critical'], 
                                       weights=[0.6, 0.3, 0.1])[0],
                affected_sensors=['*'] if random.random() > 0.5 else random.sample(
                    list(self.sensor_generators.keys()), 
                    min(random.randint(1, 3), len(self.sensor_generators))
                ),
                type=random.choice(['spike', 'drop', 'noise', 'drift']),
                magnitude=random.uniform(0.5, 2.0)
            )
            incidents_to_add.append(incident)
        
        # Add incidents to all sensor generators
        for generator in self.sensor_generators.values():
            for incident in incidents_to_add:
                generator.add_incident(incident)
        
        return incidents_to_add
    
    def generate(self, start_date: datetime, output_dir: str) -> Dict:
        """Generate and save historical data for this twin"""
        all_data = []
        
        for sensor_id, generator in self.sensor_generators.items():
            sensor_data = generator.generate(start_date)
            all_data.extend(sensor_data)
        
        # Save to CSV
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{self.twin_id}_history.csv"
        filepath = os.path.join(output_dir, filename)
        
        if all_data:
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'timestamp', 'sensor_id', 'sensor_name', 'unit', 'value', 'status'
                ])
                writer.writeheader()
                writer.writerows(all_data)
            
            logger.info(f"Generated {len(all_data)} readings for {self.twin_name} -> {filename}")
        
        return {
            'twin_id': self.twin_id,
            'twin_name': self.twin_name,
            'file': filepath,
            'total_readings': len(all_data)
        }


def generate_all_historical_data(
    config_path: str = "demo_twins.json",
    output_dir: str = "historical",
    days: int = 30,
    start_date: Optional[datetime] = None
) -> List[Dict]:
    """Generate historical data for all twins"""
    
    # Load twin configurations
    with open(config_path, 'r') as f:
        data = json.load(f)
    
    # Set start date (30 days ago from now)
    if start_date is None:
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Generate for each twin
    results = []
    for twin_config in data['twins']:
        generator = TwinHistoryGenerator(twin_config, days)
        generator.generate_incidents()  # Add random incidents
        result = generator.generate(start_date, output_dir)
        results.append(result)
    
    # Generate summary
    summary = {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'start_date': start_date.isoformat(),
        'end_date': (start_date + timedelta(days=days)).isoformat(),
        'days': days,
        'twins': results
    }
    
    summary_path = os.path.join(output_dir, 'generation_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Generation complete. Summary saved to {summary_path}")
    
    return results


def generate_incidents_log(output_dir: str = "historical"):
    """Generate a human-readable incidents log"""
    incidents_log = []
    
    incidents_log.append("# Historical Data Incidents Log\n")
    incidents_log.append("This file documents the simulated incidents in the historical data.\n\n")
    
    incidents_log.append("## Typical Incident Types:\n")
    incidents_log.append("- **spike**: Sudden increase in sensor values\n")
    incidents_log.append("- **drop**: Sudden decrease in sensor values\n")
    incidents_log.append("- **noise**: Increased random variation\n")
    incidents_log.append("- **drift**: Gradual deviation from normal values\n\n")
    
    incidents_log.append("## Severity Levels:\n")
    incidents_log.append("- **minor**: Small effect, quick recovery\n")
    incidents_log.append("- **major**: Significant effect, requires attention\n")
    incidents_log.append("- **critical**: Severe effect, immediate action needed\n\n")
    
    incidents_log.append("---\n")
    incidents_log.append("*Note: Incidents are randomly generated each time history is regenerated.*\n")
    
    with open(os.path.join(output_dir, 'INCIDENTS.md'), 'w') as f:
        f.writelines(incidents_log)


def main():
    parser = argparse.ArgumentParser(description="Generate historical data for Digital Twins")
    parser.add_argument('--config', default='demo_twins.json',
                       help='Path to twins configuration file')
    parser.add_argument('--output', default='historical',
                       help='Output directory for CSV files')
    parser.add_argument('--days', type=int, default=30,
                       help='Number of days of historical data')
    parser.add_argument('--start-date', type=str, default=None,
                       help='Start date (YYYY-MM-DD format)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse start date if provided
    start_date = None
    if args.start_date:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        start_date = start_date.replace(tzinfo=timezone.utc)
    
    # Generate historical data
    generate_all_historical_data(
        config_path=args.config,
        output_dir=args.output,
        days=args.days,
        start_date=start_date
    )
    
    # Generate incidents documentation
    generate_incidents_log(args.output)
    
    print(f"\nHistorical data generation complete!")
    print(f"Files saved to: {args.output}/")
    print(f"Total readings: {args.days * 24} hours per sensor")


if __name__ == "__main__":
    main()
