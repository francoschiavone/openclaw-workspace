#!/usr/bin/env python3
"""
Scenario: Recovery After Maintenance

Simulates equipment recovery after maintenance intervention.
- Starts with degraded/failing equipment
- Simulates maintenance intervention
- Gradual return to normal operation
- Demonstrates maintenance effectiveness tracking
"""

import sys
import time
import argparse
import logging

sys.path.insert(0, '.')

from simulator import (
    SimulationController, SimulationMode, ConsolePublisher,
    RESTPublisher, MQTTPublisher
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scenario_recovery')


class RecoveryScenarioController(SimulationController):
    """Extended controller with recovery simulation capabilities"""
    
    def __init__(self, config_path: str = "demo_twins.json"):
        super().__init__(config_path)
        self.under_maintenance = set()
        self.maintenance_complete = set()
    
    def start_maintenance(self, twin_id: str):
        """Start maintenance on a twin"""
        if twin_id in self.twins:
            twin = self.twins[twin_id]
            twin.status = 'maintenance'
            twin.mode = SimulationMode.RECOVERY
            self.under_maintenance.add(twin_id)
            logger.info(f"🔧 MAINTENANCE STARTED: {twin.name}")
    
    def complete_maintenance(self, twin_id: str):
        """Complete maintenance on a twin"""
        if twin_id in self.twins and twin_id in self.under_maintenance:
            twin = self.twins[twin_id]
            
            # Reset degradation to start recovery
            for simulator in twin.sensor_simulators.values():
                simulator.set_degradation(0.8)  # Start recovery from high degradation
            
            twin.degradation_start_time = None  # Reset to start recovery timer
            self.under_maintenance.remove(twin_id)
            self.maintenance_complete.add(twin_id)
            logger.info(f"✅ MAINTENANCE COMPLETE: {twin.name} - Recovery starting")


def run_recovery_scenario(
    duration: float = 150.0,
    interval: float = 1.0,
    rest_url: str = None,
    mqtt_broker: str = None,
    console: bool = True,
    maintenance_time: float = 30.0,  # When to start maintenance
    maintenance_duration: float = 30.0,  # How long maintenance takes
):
    """
    Run the recovery after maintenance scenario.
    
    Timeline:
    - 0-30s: Degraded operation (starting condition)
    - 30-60s: Maintenance intervention
    - 60-150s: Recovery to normal operation
    """
    logger.info("=" * 60)
    logger.info("SCENARIO: Recovery After Maintenance")
    logger.info("=" * 60)
    logger.info("Description: Equipment recovery after maintenance")
    logger.info("Use case: Maintenance effectiveness tracking")
    logger.info(f"Duration: {duration} seconds")
    logger.info(f"Maintenance starts at: {maintenance_time} seconds")
    logger.info(f"Maintenance duration: {maintenance_duration} seconds")
    logger.info("-" * 60)
    
    # Create controller
    controller = RecoveryScenarioController('demo_twins.json')
    controller.update_interval = interval
    
    # Start with all twins in FAILURE mode (degraded state)
    controller.set_mode(SimulationMode.FAILURE)
    
    # Set high initial degradation
    for twin in controller.twins.values():
        for simulator in twin.sensor_simulators.values():
            simulator.set_degradation(0.85)  # Start with high degradation
        twin.status = 'warning'
    
    # Target twins for maintenance
    maintenance_targets = ['twin-001', 'twin-003']  # CNC and Conveyor
    
    # Add publishers
    if console:
        controller.add_publisher(ConsolePublisher(verbose=True))
    if rest_url:
        controller.add_publisher(RESTPublisher(base_url=rest_url))
    if mqtt_broker:
        controller.add_publisher(MQTTPublisher(broker=mqtt_broker))
    
    logger.info("Starting recovery scenario simulation...")
    logger.info("Timeline:")
    logger.info(f"  0-{maintenance_time}s: Degraded operation")
    logger.info(f"  {maintenance_time}s: Maintenance begins")
    logger.info(f"  {maintenance_time + maintenance_duration}s: Maintenance complete")
    logger.info(f"  {maintenance_time + maintenance_duration}-{duration}s: Recovery to normal")
    logger.info("-" * 60)
    
    start_time = time.time()
    maintenance_started = False
    maintenance_completed = False
    
    try:
        iteration = 0
        while controller.running:
            elapsed = time.time() - start_time
            
            if duration and elapsed >= duration:
                logger.info(f"Scenario completed after {duration} seconds")
                break
            
            # Start maintenance
            if not maintenance_started and elapsed >= maintenance_time:
                for twin_id in maintenance_targets:
                    controller.start_maintenance(twin_id)
                maintenance_started = True
            
            # Complete maintenance
            if (maintenance_started and not maintenance_completed and 
                elapsed >= maintenance_time + maintenance_duration):
                for twin_id in maintenance_targets:
                    controller.complete_maintenance(twin_id)
                maintenance_completed = True
            
            # Update all twins
            for twin_id, twin in controller.twins.items():
                data = twin.update(elapsed)
                
                # Log status changes
                if twin_id in controller.maintenance_complete:
                    if twin.status == 'operational':
                        logger.info(f"✨ RECOVERED: {twin.name}")
                        controller.maintenance_complete.remove(twin_id)
                
                # Publish
                for publisher in controller.publishers:
                    publisher.publish(data)
            
            # Progress logging
            iteration += 1
            if iteration % 20 == 0:
                progress = (elapsed / duration) * 100 if duration else 0
                phase = "Degraded"
                if elapsed >= maintenance_time + maintenance_duration:
                    phase = "Recovery"
                elif elapsed >= maintenance_time:
                    phase = "Maintenance"
                logger.info(f"Phase: {phase} | Progress: {progress:.1f}% | Elapsed: {elapsed:.0f}s")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Scenario stopped by user")
    finally:
        controller.stop()
    
    logger.info("=" * 60)
    logger.info("SCENARIO COMPLETE: Recovery After Maintenance")
    logger.info("=" * 60)
    logger.info("Summary: Recovery scenario demonstrates:")
    logger.info("  - How sensor values return to normal after maintenance")
    logger.info("  - Tracking maintenance effectiveness")
    logger.info("  - Status progression: WARNING -> MAINTENANCE -> OPERATIONAL")
    logger.info("  - Value of maintenance scheduling based on condition")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Recovery After Maintenance Scenario")
    parser.add_argument('--duration', type=float, default=150.0,
                       help='Scenario duration in seconds')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Update interval in seconds')
    parser.add_argument('--maintenance-time', type=float, default=30.0,
                       help='Time to start maintenance (seconds)')
    parser.add_argument('--maintenance-duration', type=float, default=30.0,
                       help='Duration of maintenance (seconds)')
    parser.add_argument('--rest-url', default=None,
                       help='REST API base URL')
    parser.add_argument('--mqtt-broker', default=None,
                       help='MQTT broker address')
    parser.add_argument('--no-console', action='store_true',
                       help='Disable console output')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    run_recovery_scenario(
        duration=args.duration,
        interval=args.interval,
        rest_url=args.rest_url,
        mqtt_broker=args.mqtt_broker,
        console=not args.no_console,
        maintenance_time=args.maintenance_time,
        maintenance_duration=args.maintenance_duration
    )


if __name__ == "__main__":
    main()
