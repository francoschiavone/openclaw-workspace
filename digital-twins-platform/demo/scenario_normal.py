#!/usr/bin/env python3
"""
Scenario: Normal Operation

Simulates normal operating conditions for all digital twins.
- All equipment running within normal parameters
- Minor fluctuations typical of day-to-day operations
- All sensors within normal ranges
"""

import sys
import time
import argparse
import logging

# Add parent directory to path
sys.path.insert(0, '.')

from simulator import (
    SimulationController, SimulationMode, ConsolePublisher,
    RESTPublisher, MQTTPublisher
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('scenario_normal')


def run_normal_scenario(
    duration: float = 60.0,
    interval: float = 1.0,
    rest_url: str = None,
    mqtt_broker: str = None,
    console: bool = True
):
    """
    Run the normal operation scenario.
    
    In this scenario:
    - All twins operate in NORMAL mode
    - Sensors show typical day-to-day variations
    - Temperature, vibration, power all within normal bounds
    - No anomalies or warnings
    """
    logger.info("=" * 60)
    logger.info("SCENARIO: Normal Operation")
    logger.info("=" * 60)
    logger.info("Description: All equipment running within normal parameters")
    logger.info(f"Duration: {duration} seconds")
    logger.info(f"Update interval: {interval} seconds")
    logger.info("-" * 60)
    
    # Create controller
    controller = SimulationController('demo_twins.json')
    controller.update_interval = interval
    
    # Set all twins to NORMAL mode
    controller.set_mode(SimulationMode.NORMAL)
    
    # Add publishers
    if console:
        controller.add_publisher(ConsolePublisher(verbose=True))
    if rest_url:
        controller.add_publisher(RESTPublisher(base_url=rest_url))
    if mqtt_broker:
        controller.add_publisher(MQTTPublisher(broker=mqtt_broker))
    
    # Run simulation
    logger.info("Starting normal operation simulation...")
    logger.info("Press Ctrl+C to stop early")
    logger.info("-" * 60)
    
    try:
        controller.run(duration=duration)
    except KeyboardInterrupt:
        logger.info("Scenario stopped by user")
    
    logger.info("=" * 60)
    logger.info("SCENARIO COMPLETE: Normal Operation")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Normal Operation Scenario")
    parser.add_argument('--duration', type=float, default=60.0,
                       help='Scenario duration in seconds')
    parser.add_argument('--interval', type=float, default=1.0,
                       help='Update interval in seconds')
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
    
    run_normal_scenario(
        duration=args.duration,
        interval=args.interval,
        rest_url=args.rest_url,
        mqtt_broker=args.mqtt_broker,
        console=not args.no_console
    )


if __name__ == "__main__":
    main()
