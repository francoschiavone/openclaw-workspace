#!/usr/bin/env python3
"""
Scenario: Equipment Degradation

Simulates gradual equipment degradation over time.
- Slow increase in temperature and vibration
- Gradual decrease in efficiency
- Warning thresholds approached but not exceeded initially
- Demonstrates predictive maintenance use case
"""

import sys
import time
import argparse
import logging
import random

sys.path.insert(0, '.')

from simulator import (
    SimulationController, SimulationMode, ConsolePublisher,
    RESTPublisher, MQTTPublisher, DigitalTwinSimulator
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scenario_degradation')


def run_degradation_scenario(
    duration: float = 120.0,
    interval: float = 1.0,
    rest_url: str = None,
    mqtt_broker: str = None,
    console: bool = True,
    degradation_rate: float = 0.01  # Degradation per second
):
    """
    Run the equipment degradation scenario.
    
    In this scenario:
    - Starts with normal operation
    - Gradually introduces degradation
    - Temperature, vibration, and power consumption slowly increase
    - Equipment efficiency decreases
    - Warning and critical thresholds may be reached
    - Demonstrates why predictive maintenance is important
    """
    logger.info("=" * 60)
    logger.info("SCENARIO: Equipment Degradation")
    logger.info("=" * 60)
    logger.info("Description: Gradual equipment degradation over time")
    logger.info("Use case: Predictive maintenance demonstration")
    logger.info(f"Duration: {duration} seconds")
    logger.info(f"Degradation rate: {degradation_rate}/s")
    logger.info("-" * 60)
    
    # Create controller
    controller = SimulationController('demo_twins.json')
    controller.update_interval = interval
    
    # Set all twins to DEGRADATION mode
    controller.set_mode(SimulationMode.DEGRADATION)
    
    # Customize degradation duration for selected twins
    # Some twins degrade faster than others
    fast_degrading = ['twin-001', 'twin-003']  # CNC and Conveyor degrade faster
    
    for twin_id, twin in controller.twins.items():
        if twin_id in fast_degrading:
            twin.degradation_duration = duration * 0.5  # Reach max degradation in half the time
        else:
            twin.degradation_duration = duration * 0.8  # Slower degradation
    
    # Add publishers
    if console:
        controller.add_publisher(ConsolePublisher(verbose=True))
    if rest_url:
        controller.add_publisher(RESTPublisher(base_url=rest_url))
    if mqtt_broker:
        controller.add_publisher(MQTTPublisher(broker=mqtt_broker))
    
    # Run simulation
    logger.info("Starting degradation simulation...")
    logger.info("Watch for:")
    logger.info("  - Increasing temperatures")
    logger.info("  - Rising vibration levels")
    logger.info("  - Decreasing efficiency")
    logger.info("  - Status changes from OPERATIONAL -> WARNING -> CRITICAL")
    logger.info("-" * 60)
    
    start_time = time.time()
    
    try:
        iteration = 0
        while controller.running:
            elapsed = time.time() - start_time
            
            if duration and elapsed >= duration:
                logger.info(f"Scenario completed after {duration} seconds")
                break
            
            # Update all twins
            for twin_id, twin in controller.twins.items():
                data = twin.update(elapsed)
                
                # Publish
                for publisher in controller.publishers:
                    publisher.publish(data)
            
            # Log progress every 10 iterations
            iteration += 1
            if iteration % 10 == 0:
                progress = (elapsed / duration) * 100 if duration else 0
                logger.info(f"Progress: {progress:.1f}% - Elapsed: {elapsed:.0f}s")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        logger.info("Scenario stopped by user")
    finally:
        controller.stop()
    
    logger.info("=" * 60)
    logger.info("SCENARIO COMPLETE: Equipment Degradation")
    logger.info("=" * 60)
    logger.info("Summary: Equipment degradation scenario demonstrates:")
    logger.info("  - How sensor values change over time with wear")
    logger.info("  - Warning signs before failure")
    logger.info("  - Value of continuous monitoring")
    logger.info("  - Predictive maintenance opportunities")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Equipment Degradation Scenario")
    parser.add_argument('--duration', type=float, default=120.0,
                       help='Scenario duration in seconds')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Update interval in seconds')
    parser.add_argument('--degradation-rate', type=float, default=0.01,
                       help='Degradation rate per second')
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
    
    run_degradation_scenario(
        duration=args.duration,
        interval=args.interval,
        rest_url=args.rest_url,
        mqtt_broker=args.mqtt_broker,
        console=not args.no_console,
        degradation_rate=args.degradation_rate
    )


if __name__ == "__main__":
    main()
