"""
Anomaly Detection Module
Detects anomalies in sensor data using statistical and ML methods
"""

import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    SPIKE = "spike"
    DROP = "drop"
    DRIFT = "drift"
    OSCILLATION = "oscillation"
    STUCK_VALUE = "stuck_value"
    OUT_OF_RANGE = "out_of_range"
    PATTERN_CHANGE = "pattern_change"


class AnomalySeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AnomalyResult:
    """Result of anomaly detection"""
    is_anomaly: bool
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    sensor_id: str
    sensor_name: str
    value: float
    expected_range: Tuple[float, float]
    deviation: float  # How far from expected (in std devs)
    timestamp: datetime
    description: str = ""
    possible_causes: List[str] = field(default_factory=list)


def detect_anomalies(
    sensor_data: List[Dict[str, Any]],
    baseline: Optional[Dict[str, Dict]] = None,
    sensitivity: str = "medium",
) -> List[AnomalyResult]:
    """
    Detect anomalies in sensor readings.
    
    Args:
        sensor_data: List of sensor readings with id, name, value, min, max
        baseline: Optional baseline statistics for each sensor
        sensitivity: Detection sensitivity (low, medium, high)
        
    Returns:
        List of detected anomalies
    """
    anomalies = []
    
    # Sensitivity thresholds (in standard deviations)
    thresholds = {
        "low": 3.0,
        "medium": 2.0,
        "high": 1.5,
    }
    threshold = thresholds.get(sensitivity, 2.0)
    
    for reading in sensor_data:
        sensor_id = reading.get("id", reading.get("sensor_id", "unknown"))
        sensor_name = reading.get("name", sensor_id)
        value = reading.get("value", reading.get("current_value"))
        min_val = reading.get("min", 0)
        max_val = reading.get("max", 100)
        warning_threshold = reading.get("warning_threshold")
        critical_threshold = reading.get("critical_threshold")
        
        if value is None:
            continue
        
        # Get or calculate baseline
        if baseline and sensor_id in baseline:
            base = baseline[sensor_id]
            mean = base.get("mean", (min_val + max_val) / 2)
            std = base.get("std", (max_val - min_val) / 6)
        else:
            # Use sensor range as baseline
            mean = (min_val + max_val) / 2
            std = (max_val - min_val) / 6 if max_val > min_val else 1
        
        # Calculate deviation
        deviation = abs(value - mean) / (std + 1e-6)
        
        # Check for different anomaly types
        anomaly = None
        
        # Out of range check
        if value < min_val or value > max_val:
            anomaly = AnomalyResult(
                is_anomaly=True,
                anomaly_type=AnomalyType.OUT_OF_RANGE,
                severity=AnomalySeverity.CRITICAL,
                sensor_id=sensor_id,
                sensor_name=sensor_name,
                value=value,
                expected_range=(min_val, max_val),
                deviation=deviation,
                timestamp=datetime.utcnow(),
                description=f"Value {value} is outside valid range [{min_val}, {max_val}]",
                possible_causes=["Sensor malfunction", "Calibration error", "Actual system fault"],
            )
        
        # Threshold-based checks
        elif critical_threshold and value > critical_threshold:
            anomaly = AnomalyResult(
                is_anomaly=True,
                anomaly_type=AnomalyType.SPIKE,
                severity=AnomalySeverity.CRITICAL,
                sensor_id=sensor_id,
                sensor_name=sensor_name,
                value=value,
                expected_range=(min_val, critical_threshold),
                deviation=deviation,
                timestamp=datetime.utcnow(),
                description=f"Value {value} exceeds critical threshold {critical_threshold}",
                possible_causes=["Equipment malfunction", "Process upset", "Safety concern"],
            )
        
        elif warning_threshold and value > warning_threshold:
            anomaly = AnomalyResult(
                is_anomaly=True,
                anomaly_type=AnomalyType.SPIKE,
                severity=AnomalySeverity.WARNING,
                sensor_id=sensor_id,
                sensor_name=sensor_name,
                value=value,
                expected_range=(min_val, warning_threshold),
                deviation=deviation,
                timestamp=datetime.utcnow(),
                description=f"Value {value} exceeds warning threshold {warning_threshold}",
                possible_causes=["Approaching limits", "Increased load", "Environmental factors"],
            )
        
        # Statistical anomaly check
        elif deviation > threshold:
            anomaly_type = AnomalyType.SPIKE if value > mean else AnomalyType.DROP
            severity = AnomalySeverity.CRITICAL if deviation > threshold * 1.5 else AnomalySeverity.WARNING
            
            anomaly = AnomalyResult(
                is_anomaly=True,
                anomaly_type=anomaly_type,
                severity=severity,
                sensor_id=sensor_id,
                sensor_name=sensor_name,
                value=value,
                expected_range=(mean - 2*std, mean + 2*std),
                deviation=deviation,
                timestamp=datetime.utcnow(),
                description=f"Value {value} deviates {deviation:.1f} std devs from normal",
                possible_causes=["Unusual operating conditions", "Sensor noise", "Emerging issue"],
            )
        
        if anomaly:
            anomalies.append(anomaly)
    
    return anomalies


def get_anomaly_score(
    value: float,
    baseline: Dict[str, float],
    thresholds: Optional[Dict[str, float]] = None,
) -> float:
    """
    Calculate anomaly score for a single value (0-1 scale).
    
    Args:
        value: The value to score
        baseline: Dictionary with 'mean' and 'std' keys
        thresholds: Optional dict with 'warning' and 'critical' thresholds
        
    Returns:
        Anomaly score from 0 (normal) to 1 (highly anomalous)
    """
    mean = baseline.get("mean", 0)
    std = baseline.get("std", 1)
    
    # Calculate z-score
    z_score = abs(value - mean) / (std + 1e-6)
    
    # Convert to 0-1 scale using sigmoid-like function
    # z=1 -> ~0.24, z=2 -> ~0.48, z=3 -> ~0.68
    score = z_score / (z_score + 2)
    
    # Boost score if thresholds are exceeded
    if thresholds:
        if "critical" in thresholds and value > thresholds["critical"]:
            score = max(score, 0.9)
        elif "warning" in thresholds and value > thresholds["warning"]:
            score = max(score, 0.6)
    
    return min(1.0, score)


def detect_patterns(
    time_series: List[float],
    window_size: int = 10,
) -> Dict[str, Any]:
    """
    Detect patterns and changes in time series data.
    
    Args:
        time_series: List of sequential values
        window_size: Size of comparison windows
        
    Returns:
        Dictionary with detected patterns
    """
    if len(time_series) < window_size * 2:
        return {"status": "insufficient_data"}
    
    patterns = {
        "trend": "stable",
        "volatility": "normal",
        "oscillation": False,
        "stuck": False,
        "change_point": None,
    }
    
    # Detect trend
    recent = time_series[-window_size:]
    previous = time_series[-2*window_size:-window_size]
    
    recent_mean = np.mean(recent)
    previous_mean = np.mean(previous)
    
    change = (recent_mean - previous_mean) / (abs(previous_mean) + 1e-6)
    
    if change > 0.1:
        patterns["trend"] = "increasing"
    elif change < -0.1:
        patterns["trend"] = "decreasing"
    
    # Detect volatility change
    recent_std = np.std(recent)
    previous_std = np.std(previous)
    
    if recent_std > previous_std * 2:
        patterns["volatility"] = "high"
    elif recent_std < previous_std * 0.5:
        patterns["volatility"] = "low"
    
    # Detect oscillation
    diffs = np.diff(recent)
    sign_changes = np.sum(np.diff(np.sign(diffs)) != 0)
    if sign_changes > len(diffs) * 0.4:
        patterns["oscillation"] = True
    
    # Detect stuck value
    if len(set(np.round(recent, 3))) <= 2:
        patterns["stuck"] = True
    
    # Detect change point (simplified)
    if abs(change) > 0.3:
        patterns["change_point"] = len(time_series) - window_size
    
    return patterns


def calculate_baseline(
    historical_data: List[Dict[str, List[float]]],
) -> Dict[str, Dict[str, float]]:
    """
    Calculate baseline statistics from historical sensor data.
    
    Args:
        historical_data: Dict mapping sensor_id to list of historical values
        
    Returns:
        Dictionary with mean and std for each sensor
    """
    baseline = {}
    
    for sensor_id, values in historical_data.items():
        if values and len(values) > 0:
            baseline[sensor_id] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "p5": float(np.percentile(values, 5)),
                "p95": float(np.percentile(values, 95)),
            }
    
    return baseline
