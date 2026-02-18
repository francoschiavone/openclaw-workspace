"""
Simulation Module
What-if simulation engine for digital twins
"""

import numpy as np
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import copy
import logging

logger = logging.getLogger(__name__)


class ScenarioType(Enum):
    LOAD_INCREASE = "load_increase"
    LOAD_DECREASE = "load_decrease"
    TEMPERATURE_SPIKE = "temperature_spike"
    EQUIPMENT_DEGRADATION = "equipment_degradation"
    MAINTENANCE = "maintenance"
    FAILURE = "failure"
    OPTIMIZATION = "optimization"
    CUSTOM = "custom"


@dataclass
class SimulationResult:
    """Result of a simulation run"""
    scenario_name: str
    scenario_type: ScenarioType
    duration: timedelta
    initial_state: Dict[str, Any]
    final_state: Dict[str, Any]
    metrics_delta: Dict[str, float]  # Change in key metrics
    events: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    success: bool = True
    confidence: float = 0.7


def simulate_scenario(
    twin_state: Dict[str, Any],
    scenario: Dict[str, Any],
    duration_hours: int = 24,
    time_step_minutes: int = 15,
) -> SimulationResult:
    """
    Run a what-if simulation on a digital twin.
    
    Args:
        twin_state: Current state of the digital twin
        scenario: Scenario definition with type and parameters
        duration_hours: Simulation duration in hours
        time_step_minutes: Time step granularity
        
    Returns:
        SimulationResult with predicted outcomes
    """
    scenario_type = ScenarioType(scenario.get("type", "custom"))
    scenario_name = scenario.get("name", f"{scenario_type.value}_scenario")
    parameters = scenario.get("parameters", {})
    
    # Deep copy initial state
    initial_state = copy.deepcopy(twin_state)
    current_state = copy.deepcopy(twin_state)
    
    # Number of simulation steps
    num_steps = int(duration_hours * 60 / time_step_minutes)
    
    # Track events and changes
    events = []
    warnings = []
    metrics_delta = {}
    
    # Get simulation function for scenario type
    sim_func = _get_simulation_function(scenario_type)
    
    # Run simulation
    for step in range(num_steps):
        step_time = timedelta(minutes=step * time_step_minutes)
        
        # Apply scenario effects
        current_state, event = sim_func(
            current_state,
            parameters,
            step,
            num_steps,
        )
        
        if event:
            event["time"] = str(step_time)
            events.append(event)
        
        # Check for warnings/thresholds
        warnings.extend(_check_thresholds(current_state, step_time))
    
    # Calculate metric changes
    metrics_delta = _calculate_deltas(initial_state, current_state)
    
    # Generate recommendations
    recommendations = _generate_simulation_recommendations(
        scenario_type,
        current_state,
        metrics_delta,
        warnings,
    )
    
    return SimulationResult(
        scenario_name=scenario_name,
        scenario_type=scenario_type,
        duration=timedelta(hours=duration_hours),
        initial_state=initial_state,
        final_state=current_state,
        metrics_delta=metrics_delta,
        events=events,
        warnings=warnings,
        recommendations=recommendations,
        success=len([w for w in warnings if "critical" in w.lower()]) == 0,
        confidence=_calculate_confidence(num_steps, len(events)),
    )


def generate_scenarios(
    base_state: Dict[str, Any],
    context: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Generate relevant scenarios to explore based on current twin state.
    
    Args:
        base_state: Current state of the digital twin
        context: Optional context (e.g., "maintenance_planning", "optimization")
        
    Returns:
        List of scenario definitions to explore
    """
    scenarios = []
    
    # Get current metrics
    sensors = base_state.get("sensors", [])
    sensor_dict = {s.get("id", s.get("name")): s for s in sensors}
    
    # Load scenarios
    load = sensor_dict.get("load_percentage", sensor_dict.get("load", {}))
    if load:
        current_load = load.get("value", load.get("current_value", 50))
        
        if current_load < 70:
            scenarios.append({
                "name": "Load Increase +20%",
                "type": "load_increase",
                "parameters": {"increase": 20},
                "description": "Test capacity for increased production",
            })
        
        if current_load > 50:
            scenarios.append({
                "name": "Load Decrease -30%",
                "type": "load_decrease", 
                "parameters": {"decrease": 30},
                "description": "Evaluate energy savings at lower load",
            })
    
    # Temperature scenarios
    temp = sensor_dict.get("temperature", sensor_dict.get("spindle_temperature", {}))
    if temp:
        scenarios.append({
            "name": "Temperature Spike (+15°C)",
            "type": "temperature_spike",
            "parameters": {"increase": 15},
            "description": "Test thermal limits and cooling capacity",
        })
    
    # Degradation scenario (always relevant)
    scenarios.append({
        "name": "Equipment Degradation (30 days)",
        "type": "equipment_degradation",
        "parameters": {"days": 30, "degradation_rate": 0.1},
        "description": "Predict state after continued operation",
    })
    
    # Maintenance scenarios
    scenarios.append({
        "name": "Post-Maintenance State",
        "type": "maintenance",
        "parameters": {"improvement": 15},
        "description": "Expected improvement after maintenance",
    })
    
    # Optimization scenario
    scenarios.append({
        "name": "Optimized Operation",
        "type": "optimization",
        "parameters": {"efficiency_gain": 10},
        "description": "Potential gains from process optimization",
    })
    
    # Failure scenario (worst case)
    scenarios.append({
        "name": "Component Failure",
        "type": "failure",
        "parameters": {"component": "primary", "severity": 0.8},
        "description": "Impact of unexpected component failure",
    })
    
    # Context-specific scenarios
    if context == "maintenance_planning":
        scenarios = [s for s in scenarios if s["type"] in ["maintenance", "equipment_degradation", "failure"]]
    elif context == "optimization":
        scenarios = [s for s in scenarios if s["type"] in ["load_increase", "load_decrease", "optimization"]]
    
    return scenarios


# Simulation functions for each scenario type

def _get_simulation_function(scenario_type: ScenarioType) -> Callable:
    """Get the appropriate simulation function for a scenario type"""
    functions = {
        ScenarioType.LOAD_INCREASE: _sim_load_change,
        ScenarioType.LOAD_DECREASE: _sim_load_change,
        ScenarioType.TEMPERATURE_SPIKE: _sim_temperature,
        ScenarioType.EQUIPMENT_DEGRADATION: _sim_degradation,
        ScenarioType.MAINTENANCE: _sim_maintenance,
        ScenarioType.FAILURE: _sim_failure,
        ScenarioType.OPTIMIZATION: _sim_optimization,
        ScenarioType.CUSTOM: _sim_custom,
    }
    return functions.get(scenario_type, _sim_custom)


def _sim_load_change(state: Dict, params: Dict, step: int, total_steps: int) -> tuple:
    """Simulate load increase/decrease effects"""
    event = None
    increase = params.get("increase", -params.get("decrease", 0))
    
    # Gradually apply load change
    progress = min(1.0, step / (total_steps * 0.2))  # Apply over first 20%
    
    for sensor in state.get("sensors", []):
        sensor_id = sensor.get("id", sensor.get("name", ""))
        
        if "load" in sensor_id.lower():
            base_value = sensor.get("current_value", sensor.get("value", 50))
            sensor["simulated_value"] = base_value + increase * progress
        
        # Temperature increases with load
        if "temp" in sensor_id.lower():
            base_temp = sensor.get("current_value", sensor.get("value", 50))
            sensor["simulated_value"] = base_temp + increase * 0.2 * progress
        
        # Power increases with load
        if "power" in sensor_id.lower():
            base_power = sensor.get("current_value", sensor.get("value", 10))
            sensor["simulated_value"] = base_power * (1 + increase/100 * progress * 0.7)
    
    if step == int(total_steps * 0.2):
        event = {"type": "load_stabilized", "message": f"Load change of {increase}% applied"}
    
    return state, event


def _sim_temperature(state: Dict, params: Dict, step: int, total_steps: int) -> tuple:
    """Simulate temperature spike"""
    event = None
    increase = params.get("increase", 10)
    
    # Temperature spike in middle of simulation
    spike_start = int(total_steps * 0.3)
    spike_end = int(total_steps * 0.5)
    
    for sensor in state.get("sensors", []):
        sensor_id = sensor.get("id", sensor.get("name", "")).lower()
        
        if "temp" in sensor_id:
            base_value = sensor.get("current_value", sensor.get("value", 50))
            
            if spike_start <= step <= spike_end:
                spike_progress = (step - spike_start) / (spike_end - spike_start)
                spike_factor = np.sin(spike_progress * np.pi)  # Bell curve
                sensor["simulated_value"] = base_value + increase * spike_factor
            else:
                sensor["simulated_value"] = base_value
    
    if step == spike_start:
        event = {"type": "temperature_spike_start", "message": "Temperature spike begins"}
    elif step == spike_end:
        event = {"type": "temperature_spike_end", "message": "Temperature returning to normal"}
    
    return state, event


def _sim_degradation(state: Dict, params: Dict, step: int, total_steps: int) -> tuple:
    """Simulate equipment degradation over time"""
    event = None
    days = params.get("days", 30)
    rate = params.get("degradation_rate", 0.1)
    
    # Linear degradation
    progress = step / total_steps
    degradation = rate * progress
    
    for sensor in state.get("sensors", []):
        sensor_id = sensor.get("id", sensor.get("name", "")).lower()
        base_value = sensor.get("current_value", sensor.get("value", 50))
        
        # Temperature increases with degradation
        if "temp" in sensor_id:
            sensor["simulated_value"] = base_value * (1 + degradation * 0.3)
        
        # Vibration increases with degradation
        if "vib" in sensor_id:
            sensor["simulated_value"] = base_value * (1 + degradation * 0.5)
        
        # Efficiency decreases
        if "efficiency" in sensor_id or "performance" in sensor_id:
            sensor["simulated_value"] = base_value * (1 - degradation * 0.2)
    
    if progress > 0.7:
        event = {"type": "degradation_warning", "message": f"Significant degradation detected ({degradation*100:.1f}%)"}
    
    return state, event


def _sim_maintenance(state: Dict, params: Dict, step: int, total_steps: int) -> tuple:
    """Simulate post-maintenance improvement"""
    event = None
    improvement = params.get("improvement", 10)
    
    # Improvement applied at start, then slight degradation
    progress = step / total_steps
    
    for sensor in state.get("sensors", []):
        sensor_id = sensor.get("id", sensor.get("name", "")).lower()
        base_value = sensor.get("current_value", sensor.get("value", 50))
        
        # Temperature improves after maintenance
        if "temp" in sensor_id:
            sensor["simulated_value"] = base_value * (1 - improvement/100 * 0.3) * (1 + progress * 0.05)
        
        # Vibration improves
        if "vib" in sensor_id:
            sensor["simulated_value"] = base_value * (1 - improvement/100 * 0.4) * (1 + progress * 0.03)
        
        # Efficiency improves
        if "efficiency" in sensor_id:
            sensor["simulated_value"] = base_value * (1 + improvement/100 * 0.2) * (1 - progress * 0.02)
    
    if step == 0:
        event = {"type": "maintenance_performed", "message": f"Maintenance performed, expecting {improvement}% improvement"}
    
    return state, event


def _sim_failure(state: Dict, params: Dict, step: int, total_steps: int) -> tuple:
    """Simulate component failure"""
    event = None
    severity = params.get("severity", 0.5)
    
    # Failure occurs at random point in simulation
    failure_point = int(total_steps * 0.6)
    
    for sensor in state.get("sensors", []):
        sensor_id = sensor.get("id", sensor.get("name", "")).lower()
        base_value = sensor.get("current_value", sensor.get("value", 50))
        
        if step >= failure_point:
            if "temp" in sensor_id:
                sensor["simulated_value"] = base_value * (1 + severity * 0.5)
            elif "vib" in sensor_id:
                sensor["simulated_value"] = base_value * (1 + severity)
            elif "power" in sensor_id:
                sensor["simulated_value"] = base_value * (1 - severity * 0.3)
            else:
                sensor["simulated_value"] = base_value
        else:
            # Warning signs before failure
            if step >= failure_point * 0.8:
                if "vib" in sensor_id:
                    sensor["simulated_value"] = base_value * 1.2
    
    if step == failure_point:
        event = {"type": "failure", "message": "Component failure occurred", "severity": "critical"}
    elif step == int(failure_point * 0.8):
        event = {"type": "warning_sign", "message": "Unusual vibration detected"}
    
    return state, event


def _sim_optimization(state: Dict, params: Dict, step: int, total_steps: int) -> tuple:
    """Simulate optimized operation"""
    event = None
    efficiency_gain = params.get("efficiency_gain", 10)
    
    progress = step / total_steps
    
    for sensor in state.get("sensors", []):
        sensor_id = sensor.get("id", sensor.get("name", "")).lower()
        base_value = sensor.get("current_value", sensor.get("value", 50))
        
        # Gradual optimization benefits
        if "power" in sensor_id:
            sensor["simulated_value"] = base_value * (1 - efficiency_gain/100 * progress * 0.6)
        elif "temp" in sensor_id:
            sensor["simulated_value"] = base_value * (1 - efficiency_gain/100 * progress * 0.2)
        elif "efficiency" in sensor_id:
            sensor["simulated_value"] = base_value * (1 + efficiency_gain/100 * progress * 0.5)
    
    if step == total_steps - 1:
        event = {"type": "optimization_complete", "message": f"Optimization achieved {efficiency_gain}% efficiency gain"}
    
    return state, event


def _sim_custom(state: Dict, params: Dict, step: int, total_steps: int) -> tuple:
    """Custom simulation (pass-through)"""
    return state, None


# Helper functions

def _check_thresholds(state: Dict, time: timedelta) -> List[str]:
    """Check for threshold violations"""
    warnings = []
    
    for sensor in state.get("sensors", []):
        simulated = sensor.get("simulated_value", sensor.get("current_value", sensor.get("value")))
        critical = sensor.get("critical_threshold")
        warning = sensor.get("warning_threshold")
        sensor_name = sensor.get("name", sensor.get("id", "unknown"))
        
        if critical and simulated > critical:
            warnings.append(f"[CRITICAL] {sensor_name} exceeded critical threshold at {time}")
        elif warning and simulated > warning:
            warnings.append(f"[WARNING] {sensor_name} exceeded warning threshold at {time}")
    
    return warnings


def _calculate_deltas(initial: Dict, final: Dict) -> Dict[str, float]:
    """Calculate changes between initial and final states"""
    deltas = {}
    
    initial_sensors = {s.get("id", s.get("name")): s for s in initial.get("sensors", [])}
    final_sensors = {s.get("id", s.get("name")): s for s in final.get("sensors", [])}
    
    for sensor_id, final_s in final_sensors.items():
        if sensor_id in initial_sensors:
            initial_val = initial_sensors[sensor_id].get("current_value", initial_sensors[sensor_id].get("value", 0))
            final_val = final_s.get("simulated_value", final_s.get("current_value", final_s.get("value", 0)))
            
            if initial_val != 0:
                deltas[sensor_id] = ((final_val - initial_val) / initial_val) * 100
    
    return deltas


def _generate_simulation_recommendations(
    scenario_type: ScenarioType,
    final_state: Dict,
    deltas: Dict[str, float],
    warnings: List[str],
) -> List[str]:
    """Generate recommendations based on simulation results"""
    recommendations = []
    
    if scenario_type == ScenarioType.LOAD_INCREASE:
        if any("critical" in w.lower() for w in warnings):
            recommendations.append("Load increase not recommended without upgrades")
        else:
            recommendations.append("Load increase feasible with current capacity")
    
    elif scenario_type == ScenarioType.EQUIPMENT_DEGRADATION:
        recommendations.append("Schedule preventive maintenance within simulation period")
        if any(v > 20 for v in deltas.values()):
            recommendations.append("Consider earlier intervention based on degradation rate")
    
    elif scenario_type == ScenarioType.FAILURE:
        recommendations.append("Implement monitoring for early warning signs")
        recommendations.append("Ensure spare parts availability for critical components")
    
    elif scenario_type == ScenarioType.OPTIMIZATION:
        recommendations.append("Proceed with optimization implementation")
        recommendations.append("Monitor results to validate projected gains")
    
    return recommendations


def _calculate_confidence(num_steps: int, num_events: int) -> float:
    """Calculate confidence score for simulation"""
    # More steps = higher confidence (up to 0.9)
    step_confidence = min(0.9, 0.5 + num_steps / 1000)
    
    # More events = slightly lower confidence (unpredictability)
    event_penalty = min(0.2, num_events * 0.02)
    
    return max(0.5, step_confidence - event_penalty)
