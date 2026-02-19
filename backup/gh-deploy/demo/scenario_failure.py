#!/usr/bin/env python3
"""
Scenario: Imminent Failure

Simulates equipment on the verge of failure with clear warning signs.
- Multiple sensors showing abnormal readings
- Critical thresholds being approached/exceeded
- High stress indicators
- Demonstrates alerting and emergency response
"""

import sys
import time
import argparse
import logging
import random

sys.path.insert(0, '.')

from simulator import (
    SimulationController, SimulationMode, ConsolePublisher,
    RESTPublisher, MQTTPublisher, SensorSimulator
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scenario_failure')


class FailureScenarioController(SimulationController):
    """Extended controller with failure simulation capabilities"""
    
    def __init__(self, config_path: str = "demo_twins.json"):
        super().__init__(config_path)
        self.failed_twins = set()
    
    def induce_failure(self, twin_id: str, failure_type: str = 'gradual'):
        """
        Induce a failure condition on a specific twin.
        
        Args:
            twin_id: ID of the twin to affect
            failure_type: 'gradual', 'sudden', 'cascade'
        """
        if twin_id not in self.twins:
            logger.warning(f"Twin {twin_id} not found")
            return
        
        twin = self.twins[twin_id]
        
        # Set degradation to high levels
        for sensor_id, simulator in twin.sensor_simulators.items():
            simulator.set_degradation(0.85)  # 85% degradation
        
        twin.status = 'critical'
        self.failed_twins.add(twin_id)
        
        logger.warning(f"FAILURE INDUCED: {twin.name} - Type: {failure_type}")
    
    def cascade_failure(self, start_twin_id: str):
        """
        Simulate a cascade failure starting from one twin.
        Affecting connected systems.
        """
        # Define cascade relationships
        cascade_map = {
            'twin-001': ['twin-002', 'twin-003'],  # CNC failure affects robot and conveyor
            'twin-004': ['twin-005'],  # HVAC North affects HVAC South
            'twin-006': ['twin-001', 'twin-002', 'twin-003'],  # Generator affects all machines
            'twin-007': ['twin-008', 'twin-009'],  # Pump affects tanks
        }
        
        if start_twin_id in cascade_map:
            affected = cascade_map[start_twin_id]
            logger.warning(f"CASCADE FAILURE: {start_twin_id} may affect: {affected}")
            
            for twin_id in affected:
                if twin_id in self.twins:
                    # Partial degradation for affected twins
                    twin = self.twins[twin_id]
                    for simulator in twin.sensor_simulators.values():
                        simulator.set_degradation(0.4)
                    twin.status = 'warning'


def run_failure_scenario(
    duration: float = 90.0,
    interval: float = 1.0,
    rest_url: str = None,
    mqtt_broker: str = None,
    console: bool = True,
    failure_time: float = 30.0,  # When to induce failure
    failure_type: str = 'gradual'
):
    """
    Run the imminent failure scenario.
    
    In this scenario:
    - Starts with normal operation
    - Failure is induced at specified time
    - Multiple sensors show critical readings
    - Demonstrates alerting and emergency response
    - Shows cascade effects on connected systems
    """
    logger.info("=" * 60)
    logger.info("SCENARIO: Imminent Failure")
    logger.info("=" * 60)
    logger.info("Description: Equipment failure with warning signs")
    logger.info("Use case: Emergency response demonstration")
    logger.info(f"Duration: {duration} seconds")
    logger.info(f"Failure induction time: {failure_time} seconds")
    logger.info(f"Failure type: {failure_type}")
    logger.info("-" * 60)
    
    # Create controller
    controller = FailureScenarioController('demo_twins.json')
    controller.update_interval = interval
    
    # Set initial mode to NORMAL
    controller.set_mode(SimulationMode.NORMAL)
    
    # Add publishers
    if console:
        controller.add_publisher(ConsolePublisher(verbose=True))
    if rest_url:
        controller.add_publisher(RESTPublisher(base_url=rest_url))
    if mqtt_broker:
        controller.add_publisher(MQTTPublisher(broker=mqtt_broker))
    
    # Target twin for failure (CNC Machine is a good demo target)
    target_twin = 'twin-001'
    
    logger.info("Starting failure scenario simulation...")
    logger.info("Timeline:")
    logger.info(f"  0-{failure_time}s: Normal operation")
    logger.info(f"  {failure_time}s: Failure induced in {target_twin}")
    logger.info(f"  {failure_time}s+: Cascade effects on connected systems")
    logger.info("-" * 60)
    logger.warning("⚠️  WATCH FOR CRITICAL ALERTS AFTER FAILURE INDUCTION")
    logger.info("-" * 60)
    
    start_time = time.time()
    failure_induced = False
    
    try:
        iteration = 0
        while controller.running:
            elapsed = time.time() - start_time
            
            if duration and elapsed >= duration:
                logger.info(f"Scenario completed after {duration} seconds")
                break
            
            # Induce failure at specified time
            if not failure_induced and elapsed >= failure_time:
                controller.induce_failure(target_twin, failure_type)
                if failure_type == 'cascade':
                    controller.cascade_failure(target_twin)
                failure_induced = True
            
            # Update all twins
            for twin_id, twin in controller.twins.items():
                data = twin.update(elapsed)
                
                # Highlight critical readings
                if twin.status == 'critical':
                    logger.error(f"🚨 CRITICAL: {twin.name}")
                
                # Publish
                for publisher in controller.publishers:
                    publisher.publish(data)
            
            iteration += 1
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Scenario stopped by user")
    finally:
        controller.stop()
    
    logger.info("=" * 60)
    logger.info("SCENARIO COMPLETE: Imminent Failure")
    logger.info("=" * 60)
    logger.info("Summary: Failure scenario demonstrates:")
    logger.info("  - Warning signs before catastrophic failure")
    logger.info("  - Critical threshold alerts")
    logger.info("  - Cascade effects on connected equipment")
    logger.info("  - Need for automated emergency responses")
    logger.info("  - Importance of real-time monitoring")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Imminent Failure Scenario")
    parser.add_argument('--duration', type=float, default=90.0,
                       help='Scenario duration in seconds')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Update interval in seconds')
    parser.add_argument('--failure-time', type=float, default=30.0,
                       help='Time to induce failure (seconds)')
    parser.add_argument('--failure-type', choices=['gradual', 'sudden', 'cascade'],
                       default='gradual', help='Type of failure simulation')
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
    
    run_failure_scenario(
        duration=args.duration,
        interval=args.interval,
        rest_url=args.rest_url,
        mqtt_broker=args.mqtt_broker,
        console=not args.no_console,
        failure_time=args.failure_time,
        failure_type=args.failure_type
    )


if __name__ == "__main__":
    main()
