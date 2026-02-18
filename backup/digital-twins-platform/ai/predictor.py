"""
Predictor Module - ML models for prediction and forecasting

Provides time series forecasting, equipment failure prediction,
and maintenance recommendation capabilities.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field

import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor

logger = logging.getLogger(__name__)


class PredictionError(Exception):
    """Base exception for prediction-related errors."""
    pass


class InsufficientDataError(PredictionError):
    """Raised when there's not enough data for prediction."""
    pass


class InvalidInputError(PredictionError):
    """Raised when input data is invalid or malformed."""
    pass


@dataclass
class SensorReading:
    """Represents a single sensor reading."""
    timestamp: datetime
    value: float
    sensor_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class FailurePrediction:
    """Result of a failure prediction."""
    probability: float
    confidence: float
    time_to_failure_hours: Optional[float]
    risk_factors: list[str]
    recommended_actions: list[str]


@dataclass
class MaintenanceRecommendation:
    """Result of maintenance prediction."""
    urgency: str  # "low", "medium", "high", "critical"
    maintenance_type: str
    estimated_due_date: datetime
    confidence: float
    reasoning: str
    parts_needed: list[str]


def _validate_sensor_history(
    sensor_history: list[dict],
    min_readings: int = 10
) -> list[SensorReading]:
    """
    Validate and convert sensor history to SensorReading objects.
    
    Args:
        sensor_history: List of dicts with 'timestamp' and 'value' keys
        min_readings: Minimum number of readings required
        
    Returns:
        List of validated SensorReading objects
        
    Raises:
        InvalidInputError: If input format is invalid
        InsufficientDataError: If not enough readings
    """
    if not sensor_history:
        raise InvalidInputError("sensor_history cannot be empty")
    
    if not isinstance(sensor_history, list):
        raise InvalidInputError("sensor_history must be a list")
    
    if len(sensor_history) < min_readings:
        raise InsufficientDataError(
            f"Need at least {min_readings} readings, got {len(sensor_history)}"
        )
    
    readings = []
    for i, item in enumerate(sensor_history):
        if not isinstance(item, dict):
            raise InvalidInputError(f"Item {i} is not a dict")
        
        if 'value' not in item:
            raise InvalidInputError(f"Item {i} missing 'value' key")
        
        try:
            timestamp = item.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            elif isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(timestamp)
            elif timestamp is None:
                timestamp = datetime.now()
            elif not isinstance(timestamp, datetime):
                raise ValueError(f"Invalid timestamp type: {type(timestamp)}")
            
            readings.append(SensorReading(
                timestamp=timestamp,
                value=float(item['value']),
                sensor_id=item.get('sensor_id'),
                metadata=item.get('metadata', {})
            ))
        except (ValueError, TypeError) as e:
            raise InvalidInputError(f"Item {i} has invalid data: {e}")
    
    return readings


def predict_failure(sensor_history: list[dict]) -> dict:
    """
    Predict equipment failure probability based on sensor history.
    
    Uses statistical analysis and trend detection to estimate
    the probability of equipment failure.
    
    Args:
        sensor_history: List of dicts with 'timestamp' and 'value' keys.
                       Each dict represents a sensor reading over time.
                       Expected to include multiple sensor types.
        
    Returns:
        dict containing:
            - probability: float (0.0 to 1.0) - Failure probability
            - confidence: float (0.0 to 1.0) - Model confidence
            - time_to_failure_hours: float or None - Estimated hours until failure
            - risk_factors: list of str - Identified risk factors
            - recommended_actions: list of str - Recommended actions
            
    Raises:
        PredictionError: If prediction fails
        InvalidInputError: If input format is invalid
        InsufficientDataError: If not enough data points
        
    Example:
        >>> history = [
        ...     {"timestamp": "2024-01-01T10:00:00", "value": 45.2},
        ...     {"timestamp": "2024-01-01T10:05:00", "value": 46.1},
        ...     # ... more readings
        ... ]
        >>> result = predict_failure(history)
        >>> print(result["probability"])
        0.15
    """
    try:
        readings = _validate_sensor_history(sensor_history, min_readings=10)
        
        # Extract values and timestamps
        values = np.array([r.value for r in readings])
        timestamps = [r.timestamp for r in readings]
        
        # Sort by timestamp
        sorted_indices = np.argsort([t.timestamp() for t in timestamps])
        values = values[sorted_indices]
        
        risk_factors = []
        recommended_actions = []
        
        # Statistical analysis
        mean_value = np.mean(values)
        std_value = np.std(values)
        trend = np.polyfit(range(len(values)), values, 1)[0]
        
        # Detect anomalies in recent data
        recent_values = values[-10:] if len(values) >= 10 else values
        recent_mean = np.mean(recent_values)
        recent_std = np.std(recent_values)
        
        # Risk factor: High variance
        coefficient_of_variation = std_value / mean_value if mean_value != 0 else 0
        if coefficient_of_variation > 0.3:
            risk_factors.append("High variability in sensor readings")
            recommended_actions.append("Investigate sensor calibration")
        
        # Risk factor: Upward trend (assuming higher values indicate degradation)
        if trend > 0:
            trend_strength = "strong" if trend > (std_value / len(values) * 0.1) else "moderate"
            risk_factors.append(f"{trend_strength.capitalize()} upward trend detected")
            recommended_actions.append("Schedule preventive maintenance")
        
        # Risk factor: Recent spike
        if len(recent_values) >= 3:
            if np.max(recent_values[-3:]) > mean_value + 2 * std_value:
                risk_factors.append("Recent spike in readings")
                recommended_actions.append("Inspect for immediate issues")
        
        # Risk factor: Sustained high values
        if recent_mean > mean_value + std_value:
            risk_factors.append("Sustained elevated readings")
        
        # Calculate base probability from risk factors
        base_probability = min(0.9, len(risk_factors) * 0.15)
        
        # Adjust for trend severity
        if trend > 0:
            trend_adjustment = min(0.3, abs(trend) / (std_value + 0.001) * 0.1)
            base_probability += trend_adjustment
        
        # Adjust for variance
        if coefficient_of_variation > 0.5:
            base_probability += 0.1
        
        # Clamp probability
        probability = max(0.0, min(1.0, base_probability))
        
        # Calculate confidence based on data quality
        confidence = min(0.95, 0.5 + len(readings) * 0.01)
        if coefficient_of_variation > 0.4:
            confidence *= 0.8  # Lower confidence with high variance
        
        # Estimate time to failure (simplified model)
        time_to_failure_hours = None
        if probability > 0.3 and trend > 0:
            # Extrapolate to threshold
            threshold = mean_value + 3 * std_value
            if values[-1] < threshold:
                hours_to_threshold = (threshold - values[-1]) / (trend * 12)  # Assuming hourly readings
                time_to_failure_hours = max(1, hours_to_threshold)
        
        # Default recommendations if none generated
        if not recommended_actions:
            recommended_actions.append("Continue monitoring")
        
        if not risk_factors:
            risk_factors.append("No significant risk factors detected")
        
        result = FailurePrediction(
            probability=round(probability, 3),
            confidence=round(confidence, 3),
            time_to_failure_hours=round(time_to_failure_hours, 1) if time_to_failure_hours else None,
            risk_factors=risk_factors,
            recommended_actions=recommended_actions
        )
        
        logger.info(f"Failure prediction completed: probability={probability:.2%}")
        
        return {
            "probability": result.probability,
            "confidence": result.confidence,
            "time_to_failure_hours": result.time_to_failure_hours,
            "risk_factors": result.risk_factors,
            "recommended_actions": result.recommended_actions
        }
        
    except (PredictionError, InvalidInputError, InsufficientDataError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in predict_failure: {e}")
        raise PredictionError(f"Prediction failed: {e}") from e


def predict_maintenance(equipment_data: dict) -> dict:
    """
    Predict maintenance needs based on equipment data.
    
    Analyzes equipment parameters, usage patterns, and historical
    maintenance records to predict when and what maintenance is needed.
    
    Args:
        equipment_data: dict containing:
            - operating_hours: float - Total operating hours
            - last_maintenance: str (ISO date) - Last maintenance date
            - maintenance_history: list of dicts - Historical maintenance records
            - sensor_data: list of dicts - Recent sensor readings
            - equipment_type: str - Type of equipment (optional)
            - rated_lifetime_hours: float - Manufacturer rated lifetime (optional)
            
    Returns:
        dict containing:
            - urgency: str - "low", "medium", "high", or "critical"
            - maintenance_type: str - Type of maintenance needed
            - estimated_due_date: str (ISO date) - When maintenance is due
            - confidence: float - Prediction confidence
            - reasoning: str - Explanation for the recommendation
            - parts_needed: list of str - Parts that may be needed
            
    Raises:
        PredictionError: If prediction fails
        InvalidInputError: If input format is invalid
        
    Example:
        >>> equipment = {
        ...     "operating_hours": 5000,
        ...     "last_maintenance": "2023-06-15",
        ...     "maintenance_history": [...],
        ...     "sensor_data": [...]
        ... }
        >>> result = predict_maintenance(equipment)
        >>> print(result["urgency"])
        "medium"
    """
    try:
        if not isinstance(equipment_data, dict):
            raise InvalidInputError("equipment_data must be a dict")
        
        # Extract and validate required fields
        operating_hours = equipment_data.get('operating_hours', 0)
        if not isinstance(operating_hours, (int, float)):
            raise InvalidInputError("operating_hours must be a number")
        
        # Parse last maintenance date
        last_maintenance = equipment_data.get('last_maintenance')
        if last_maintenance:
            if isinstance(last_maintenance, str):
                last_maintenance_date = datetime.fromisoformat(
                    last_maintenance.replace('Z', '+00:00')
                )
            elif isinstance(last_maintenance, datetime):
                last_maintenance_date = last_maintenance
            else:
                last_maintenance_date = datetime.now() - timedelta(days=90)
        else:
            last_maintenance_date = datetime.now() - timedelta(days=90)
        
        days_since_maintenance = (datetime.now() - last_maintenance_date).days
        
        # Get optional parameters
        rated_lifetime = equipment_data.get('rated_lifetime_hours', 10000)
        equipment_type = equipment_data.get('equipment_type', 'general')
        maintenance_history = equipment_data.get('maintenance_history', [])
        
        # Analyze maintenance history
        avg_interval_days = 90  # Default
        if maintenance_history and len(maintenance_history) >= 2:
            intervals = []
            sorted_history = sorted(
                maintenance_history,
                key=lambda x: x.get('date', ''),
                reverse=True
            )
            for i in range(len(sorted_history) - 1):
                try:
                    d1 = datetime.fromisoformat(sorted_history[i]['date'].replace('Z', '+00:00'))
                    d2 = datetime.fromisoformat(sorted_history[i+1]['date'].replace('Z', '+00:00'))
                    intervals.append((d1 - d2).days)
                except (KeyError, ValueError):
                    continue
            if intervals:
                avg_interval_days = np.mean(intervals)
        
        # Calculate urgency factors
        urgency_score = 0
        reasoning_parts = []
        parts_needed = []
        
        # Factor 1: Operating hours vs rated lifetime
        lifetime_ratio = operating_hours / rated_lifetime if rated_lifetime else 0
        if lifetime_ratio > 0.9:
            urgency_score += 0.4
            reasoning_parts.append("Equipment approaching end of rated lifetime")
            parts_needed.append("Replacement unit assessment")
        elif lifetime_ratio > 0.7:
            urgency_score += 0.2
            reasoning_parts.append("Equipment in later stages of operational life")
        
        # Factor 2: Time since last maintenance
        if days_since_maintenance > avg_interval_days * 1.5:
            urgency_score += 0.3
            reasoning_parts.append(f"Overdue for maintenance by {days_since_maintenance - avg_interval_days:.0f} days")
        elif days_since_maintenance > avg_interval_days:
            urgency_score += 0.15
            reasoning_parts.append("Maintenance interval exceeded")
        
        # Factor 3: Operating hours since last maintenance
        hours_since_last = operating_hours
        if maintenance_history:
            try:
                last_record = max(
                    maintenance_history,
                    key=lambda x: x.get('operating_hours', 0)
                )
                hours_since_last = operating_hours - last_record.get('operating_hours', 0)
            except (ValueError, KeyError):
                pass
        
        if hours_since_last > 2000:
            urgency_score += 0.2
            reasoning_parts.append("High operating hours since last service")
            parts_needed.extend(["Oil/filter change", "Wear inspection"])
        
        # Factor 4: Analyze sensor data if available
        sensor_data = equipment_data.get('sensor_data', [])
        if sensor_data:
            try:
                failure_pred = predict_failure(sensor_data)
                if failure_pred['probability'] > 0.5:
                    urgency_score += 0.3
                    reasoning_parts.append("Sensor analysis indicates elevated failure risk")
                elif failure_pred['probability'] > 0.3:
                    urgency_score += 0.15
            except PredictionError:
                pass  # Sensor analysis failed, continue with other factors
        
        # Determine urgency level
        if urgency_score >= 0.7:
            urgency = "critical"
        elif urgency_score >= 0.5:
            urgency = "high"
        elif urgency_score >= 0.3:
            urgency = "medium"
        else:
            urgency = "low"
        
        # Determine maintenance type
        if urgency in ["critical", "high"]:
            maintenance_type = "Preventive maintenance (immediate)"
        elif "sensor" in str(reasoning_parts).lower():
            maintenance_type = "Diagnostic inspection"
        elif lifetime_ratio > 0.8:
            maintenance_type = "Comprehensive overhaul"
        else:
            maintenance_type = "Routine maintenance"
        
        # Calculate estimated due date
        if urgency == "critical":
            due_days = 1
        elif urgency == "high":
            due_days = 7
        elif urgency == "medium":
            due_days = 30
        else:
            due_days = max(30, avg_interval_days - days_since_maintenance)
        
        estimated_due_date = datetime.now() + timedelta(days=due_days)
        
        # Calculate confidence
        confidence = 0.7
        if maintenance_history:
            confidence += 0.1
        if sensor_data:
            confidence += 0.1
        confidence = min(0.95, confidence)
        
        # Default reasoning if none generated
        if not reasoning_parts:
            reasoning_parts.append("Based on standard maintenance intervals")
        
        if not parts_needed:
            parts_needed = ["Standard maintenance kit"]
        
        result = MaintenanceRecommendation(
            urgency=urgency,
            maintenance_type=maintenance_type,
            estimated_due_date=estimated_due_date,
            confidence=round(confidence, 3),
            reasoning="; ".join(reasoning_parts),
            parts_needed=parts_needed
        )
        
        logger.info(f"Maintenance prediction: urgency={urgency}, due={estimated_due_date.date()}")
        
        return {
            "urgency": result.urgency,
            "maintenance_type": result.maintenance_type,
            "estimated_due_date": result.estimated_due_date.isoformat(),
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "parts_needed": result.parts_needed
        }
        
    except (PredictionError, InvalidInputError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in predict_maintenance: {e}")
        raise PredictionError(f"Maintenance prediction failed: {e}") from e


def forecast_metric(
    metric_history: list[dict],
    horizon: int = 24,
    method: str = "auto"
) -> list[dict]:
    """
    Forecast a metric into the future using time series methods.
    
    Supports multiple forecasting methods and automatically selects
    the best approach based on data characteristics.
    
    Args:
        metric_history: List of dicts with 'timestamp' and 'value' keys.
                       Represents historical values of the metric.
        horizon: Number of time steps to forecast into the future.
        method: Forecasting method - "linear", "auto", or "ensemble"
        
    Returns:
        List of dicts, each containing:
            - timestamp: str (ISO format) - Forecast timestamp
            - value: float - Forecasted value
            - lower_bound: float - Lower confidence interval (95%)
            - upper_bound: float - Upper confidence interval (95%)
            
    Raises:
        PredictionError: If forecasting fails
        InvalidInputError: If input format is invalid
        InsufficientDataError: If not enough data points
        
    Example:
        >>> history = [
        ...     {"timestamp": "2024-01-01T00:00:00", "value": 100},
        ...     {"timestamp": "2024-01-01T01:00:00", "value": 102},
        ...     # ... more readings
        ... ]
        >>> forecast = forecast_metric(history, horizon=12)
        >>> print(len(forecast))
        12
    """
    try:
        if horizon < 1:
            raise InvalidInputError("horizon must be at least 1")
        
        readings = _validate_sensor_history(metric_history, min_readings=5)
        
        # Extract and sort data
        values = np.array([r.value for r in readings])
        timestamps = [r.timestamp for r in readings]
        
        sorted_pairs = sorted(zip(timestamps, values), key=lambda x: x[0])
        timestamps = [p[0] for p in sorted_pairs]
        values = np.array([p[1] for p in sorted_pairs])
        
        n = len(values)
        X = np.arange(n).reshape(-1, 1)
        
        # Determine time step from data
        if len(timestamps) >= 2:
            time_diffs = []
            for i in range(1, len(timestamps)):
                diff = (timestamps[i] - timestamps[i-1]).total_seconds()
                if diff > 0:
                    time_diffs.append(diff)
            avg_step_seconds = np.mean(time_diffs) if time_diffs else 3600
        else:
            avg_step_seconds = 3600
        
        # Select and fit model
        if method == "auto":
            # Simple model selection based on data characteristics
            if n < 10:
                method = "linear"
            elif np.std(values) / (np.mean(np.abs(values)) + 1e-10) < 0.1:
                method = "linear"  # Low variance, use linear
            else:
                method = "ensemble"
        
        if method == "linear":
            model = LinearRegression()
            model.fit(X, values)
            
            # Calculate residuals for confidence intervals
            predictions = model.predict(X)
            residuals = values - predictions
            residual_std = np.std(residuals) if len(residuals) > 1 else 1.0
            
            # Forecast
            future_X = np.arange(n, n + horizon).reshape(-1, 1)
            forecast_values = model.predict(future_X)
            
        elif method == "ensemble":
            # Use multiple models and average
            models = [
                LinearRegression(),
                Ridge(alpha=1.0)
            ]
            
            forecast_values_list = []
            residuals_all = []
            
            for m in models:
                m.fit(X, values)
                preds = m.predict(X)
                residuals_all.extend(values - preds)
                future_X = np.arange(n, n + horizon).reshape(-1, 1)
                forecast_values_list.append(m.predict(future_X))
            
            forecast_values = np.mean(forecast_values_list, axis=0)
            residual_std = np.std(residuals_all)
            
        else:
            raise InvalidInputError(f"Unknown method: {method}")
        
        # Generate timestamps for forecast
        last_timestamp = timestamps[-1]
        future_timestamps = [
            last_timestamp + timedelta(seconds=avg_step_seconds * (i + 1))
            for i in range(horizon)
        ]
        
        # Calculate confidence intervals
        # Confidence interval widens with forecast horizon
        confidence_multiplier = 1.96  # 95% confidence
        
        results = []
        for i, (ts, val) in enumerate(zip(future_timestamps, forecast_values)):
            # Uncertainty increases with horizon
            uncertainty = residual_std * np.sqrt(1 + (i + 1) / n)
            lower = val - confidence_multiplier * uncertainty
            upper = val + confidence_multiplier * uncertainty
            
            results.append({
                "timestamp": ts.isoformat(),
                "value": round(float(val), 4),
                "lower_bound": round(float(lower), 4),
                "upper_bound": round(float(upper), 4)
            })
        
        logger.info(f"Forecast completed: {horizon} steps using {method} method")
        
        return results
        
    except (PredictionError, InvalidInputError, InsufficientDataError):
        raise
    except Exception as e:
        logger.error(f"Unexpected error in forecast_metric: {e}")
        raise PredictionError(f"Forecasting failed: {e}") from e


class PredictorModel:
    """
    Persistent predictor model for stateful predictions.
    
    Allows training and saving models for repeated use.
    """
    
    def __init__(self, model_type: str = "random_forest"):
        """
        Initialize predictor model.
        
        Args:
            model_type: Type of model - "linear", "ridge", or "random_forest"
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_fitted = False
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> "PredictorModel":
        """Fit the model to training data."""
        X_scaled = self.scaler.fit_transform(X)
        
        if self.model_type == "linear":
            self.model = LinearRegression()
        elif self.model_type == "ridge":
            self.model = Ridge(alpha=1.0)
        elif self.model_type == "random_forest":
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
        
        self.model.fit(X_scaled, y)
        self.is_fitted = True
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions using fitted model."""
        if not self.is_fitted:
            raise PredictionError("Model must be fitted before prediction")
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
