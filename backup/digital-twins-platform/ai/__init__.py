"""
AI/ML Layer for Digital Twins Platform

This module provides predictive analytics, anomaly detection,
simulation capabilities, and LLM-powered natural language interfaces
for digital twin operations.

Modules:
    - predictor: ML models for failure prediction and time series forecasting
    - anomaly: Anomaly detection in sensor data
    - simulator: What-if scenario simulation engine
    - llm_interface: Natural language interface for twin queries
"""

__version__ = "1.0.0"
__author__ = "Digital Twins Platform Team"

from .predictor import (
    predict_failure,
    predict_maintenance,
    forecast_metric,
    PredictionError,
    InsufficientDataError,
    InvalidInputError as PredictorInputError,
)
from .anomaly import (
    detect_anomalies,
    get_anomaly_score,
    AnomalyDetector,
    AnomalyError,
    InvalidInputError as AnomalyInputError,
    InsufficientDataError as AnomalyInsufficientError,
)
from .simulator import (
    simulate_scenario,
    generate_scenarios,
    SimulationEngine,
    SimulationError,
    InvalidStateError,
    InvalidScenarioError,
)
from .llm_interface import (
    query_twin,
    generate_insights,
    explain_anomaly,
    LLMInterface,
    LLMError,
    ConfigurationError,
    APIError,
)

__all__ = [
    # Predictor
    "predict_failure",
    "predict_maintenance",
    "forecast_metric",
    "PredictionError",
    "InsufficientDataError",
    "PredictorInputError",
    # Anomaly
    "detect_anomalies",
    "get_anomaly_score",
    "AnomalyDetector",
    "AnomalyError",
    "AnomalyInputError",
    "AnomalyInsufficientError",
    # Simulator
    "simulate_scenario",
    "generate_scenarios",
    "SimulationEngine",
    "SimulationError",
    "InvalidStateError",
    "InvalidScenarioError",
    # LLM
    "query_twin",
    "generate_insights",
    "explain_anomaly",
    "LLMInterface",
    "LLMError",
    "ConfigurationError",
    "APIError",
]
