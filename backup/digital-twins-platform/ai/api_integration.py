"""
API Integration Module - FastAPI integration for AI/ML layer

This module provides ready-to-use FastAPI router endpoints
for integrating the AI/ML capabilities with your backend.

Usage:
    from fastapi import FastAPI
    from ai.api_integration import ai_router
    
    app = FastAPI()
    app.include_router(ai_router, prefix="/api/ai", tags=["AI/ML"])
"""

import logging
from datetime import datetime
from typing import Optional, List
from functools import wraps

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field

from .predictor import (
    predict_failure,
    predict_maintenance,
    forecast_metric,
    PredictionError,
    InsufficientDataError,
    InvalidInputError as PredictorInputError
)
from .anomaly import (
    detect_anomalies,
    get_anomaly_score,
    AnomalyError,
    InvalidInputError as AnomalyInputError,
    InsufficientDataError as AnomalyInsufficientError
)
from .simulator import (
    simulate_scenario,
    generate_scenarios,
    SimulationError,
    InvalidStateError,
    InvalidScenarioError
)
from .llm_interface import (
    query_twin,
    generate_insights,
    explain_anomaly,
    LLMError
)

logger = logging.getLogger(__name__)

# Create main router
ai_router = APIRouter()


# ============== Request/Response Models ==============

class SensorReading(BaseModel):
    """Single sensor reading."""
    timestamp: Optional[str] = None
    value: float
    sensor_id: Optional[str] = None
    metadata: Optional[dict] = None


class PredictFailureRequest(BaseModel):
    """Request for failure prediction."""
    sensor_history: List[dict] = Field(..., min_length=10)


class PredictFailureResponse(BaseModel):
    """Response from failure prediction."""
    probability: float
    confidence: float
    time_to_failure_hours: Optional[float]
    risk_factors: List[str]
    recommended_actions: List[str]


class PredictMaintenanceRequest(BaseModel):
    """Request for maintenance prediction."""
    operating_hours: float
    last_maintenance: Optional[str] = None
    maintenance_history: Optional[List[dict]] = None
    sensor_data: Optional[List[dict]] = None
    equipment_type: Optional[str] = None
    rated_lifetime_hours: Optional[float] = None


class PredictMaintenanceResponse(BaseModel):
    """Response from maintenance prediction."""
    urgency: str
    maintenance_type: str
    estimated_due_date: str
    confidence: float
    reasoning: str
    parts_needed: List[str]


class ForecastRequest(BaseModel):
    """Request for metric forecasting."""
    metric_history: List[dict] = Field(..., min_length=5)
    horizon: int = Field(default=24, ge=1, le=168)
    method: str = Field(default="auto")


class ForecastPoint(BaseModel):
    """Single forecast point."""
    timestamp: str
    value: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    """Response from forecasting."""
    forecast: List[ForecastPoint]
    method: str
    horizon: int


class DetectAnomaliesRequest(BaseModel):
    """Request for anomaly detection."""
    sensor_data: List[dict] = Field(..., min_length=5)
    baseline_data: Optional[List[dict]] = None
    method: str = Field(default="ensemble")
    sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)


class AnomalyResult(BaseModel):
    """Single detected anomaly."""
    timestamp: str
    value: float
    score: float
    severity: str
    anomaly_type: str
    description: str


class DetectAnomaliesResponse(BaseModel):
    """Response from anomaly detection."""
    anomalies: List[AnomalyResult]
    total_analyzed: int
    anomaly_count: int


class AnomalyScoreRequest(BaseModel):
    """Request for single anomaly score."""
    value: float
    baseline: dict
    method: str = Field(default="zscore")


class AnomalyScoreResponse(BaseModel):
    """Response for anomaly score."""
    score: float
    value: float
    method: str


class SimulateScenarioRequest(BaseModel):
    """Request for scenario simulation."""
    twin_state: dict
    scenario: dict
    config: Optional[dict] = None


class SimulateScenarioResponse(BaseModel):
    """Response from scenario simulation."""
    scenario_name: str
    success: bool
    outcome_state: dict
    metrics: dict
    events: List[dict]
    warnings: List[str]
    confidence: float
    execution_time_ms: float
    timestamp: str


class GenerateScenariosRequest(BaseModel):
    """Request for scenario generation."""
    base_state: dict
    scenario_types: Optional[List[str]] = None
    count: int = Field(default=5, ge=1, le=20)


class GeneratedScenario(BaseModel):
    """A generated scenario."""
    name: str
    type: str
    parameters: dict
    description: str
    priority: int
    duration_hours: Optional[float] = None
    constraints: Optional[dict] = None


class GenerateScenariosResponse(BaseModel):
    """Response from scenario generation."""
    scenarios: List[GeneratedScenario]
    count: int


class QueryTwinRequest(BaseModel):
    """Request to query twin with natural language."""
    question: str
    twin_data: dict
    additional_context: Optional[str] = None


class QueryTwinResponse(BaseModel):
    """Response from twin query."""
    answer: str
    question: str
    timestamp: str


class GenerateInsightsRequest(BaseModel):
    """Request to generate insights."""
    twin_data: dict
    focus_areas: Optional[List[str]] = None


class Insight(BaseModel):
    """A single insight."""
    category: str
    title: str
    description: str
    severity: str
    recommendation: str


class GenerateInsightsResponse(BaseModel):
    """Response from insight generation."""
    insights: List[Insight]
    count: int
    timestamp: str


class ExplainAnomalyRequest(BaseModel):
    """Request to explain an anomaly."""
    anomaly: dict
    context: dict


class ExplainAnomalyResponse(BaseModel):
    """Response from anomaly explanation."""
    explanation: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: str
    timestamp: str


# ============== Error Handling ==============

def handle_ai_errors(func):
    """Decorator to handle AI/ML errors and convert to HTTP exceptions."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (InsufficientDataError, AnomalyInsufficientError) as e:
            logger.warning(f"Insufficient data: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except (PredictorInputError, AnomalyInputError) as e:
            logger.warning(f"Invalid input: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except (PredictionError, AnomalyError) as e:
            logger.error(f"AI processing error: {e}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {e}")
        except (InvalidStateError, InvalidScenarioError) as e:
            logger.warning(f"Invalid simulation input: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except SimulationError as e:
            logger.error(f"Simulation error: {e}")
            raise HTTPException(status_code=500, detail=f"Simulation failed: {e}")
        except LLMError as e:
            logger.error(f"LLM error: {e}")
            raise HTTPException(status_code=503, detail=f"AI service unavailable: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper


# ============== Prediction Endpoints ==============

@ai_router.post("/predict/failure", response_model=PredictFailureResponse)
@handle_ai_errors
async def api_predict_failure(request: PredictFailureRequest):
    """
    Predict equipment failure probability.
    
    Analyzes sensor history to predict the probability of equipment failure,
    identify risk factors, and recommend actions.
    """
    result = predict_failure(request.sensor_history)
    return PredictFailureResponse(**result)


@ai_router.post("/predict/maintenance", response_model=PredictMaintenanceResponse)
@handle_ai_errors
async def api_predict_maintenance(request: PredictMaintenanceRequest):
    """
    Predict maintenance needs.
    
    Analyzes equipment data to predict when maintenance is needed
    and what type of maintenance should be performed.
    """
    equipment_data = request.model_dump(exclude_none=True)
    result = predict_maintenance(equipment_data)
    return PredictMaintenanceResponse(**result)


@ai_router.post("/predict/forecast", response_model=ForecastResponse)
@handle_ai_errors
async def api_forecast_metric(request: ForecastRequest):
    """
    Forecast a metric into the future.
    
    Uses time series analysis to predict future values of a metric
    with confidence intervals.
    """
    forecast = forecast_metric(
        request.metric_history,
        horizon=request.horizon,
        method=request.method
    )
    return ForecastResponse(
        forecast=[ForecastPoint(**f) for f in forecast],
        method=request.method,
        horizon=request.horizon
    )


# ============== Anomaly Detection Endpoints ==============

@ai_router.post("/anomalies/detect", response_model=DetectAnomaliesResponse)
@handle_ai_errors
async def api_detect_anomalies(request: DetectAnomaliesRequest):
    """
    Detect anomalies in sensor data.
    
    Uses statistical and ML methods to identify anomalous readings
    with severity scores and descriptions.
    """
    anomalies = detect_anomalies(
        request.sensor_data,
        baseline_data=request.baseline_data,
        method=request.method,
        sensitivity=request.sensitivity
    )
    return DetectAnomaliesResponse(
        anomalies=[AnomalyResult(**a) for a in anomalies],
        total_analyzed=len(request.sensor_data),
        anomaly_count=len(anomalies)
    )


@ai_router.post("/anomalies/score", response_model=AnomalyScoreResponse)
@handle_ai_errors
async def api_get_anomaly_score(request: AnomalyScoreRequest):
    """
    Calculate anomaly score for a single value.
    
    Returns an anomaly score (0-1) for a value compared to baseline statistics.
    """
    score = get_anomaly_score(
        request.value,
        request.baseline,
        method=request.method
    )
    return AnomalyScoreResponse(
        score=score,
        value=request.value,
        method=request.method
    )


# ============== Simulation Endpoints ==============

@ai_router.post("/simulate", response_model=SimulateScenarioResponse)
@handle_ai_errors
async def api_simulate_scenario(request: SimulateScenarioRequest):
    """
    Run a what-if simulation scenario.
    
    Simulates the effects of a scenario (stress test, failure, maintenance, etc.)
    on a digital twin state.
    """
    result = simulate_scenario(
        request.twin_state,
        request.scenario,
        config=request.config
    )
    return SimulateScenarioResponse(**result)


@ai_router.post("/simulate/generate-scenarios", response_model=GenerateScenariosResponse)
@handle_ai_errors
async def api_generate_scenarios(request: GenerateScenariosRequest):
    """
    Generate relevant scenarios to explore.
    
    Analyzes the twin state and generates meaningful scenarios
    for what-if analysis.
    """
    scenarios = generate_scenarios(
        request.base_state,
        scenario_types=request.scenario_types,
        count=request.count
    )
    return GenerateScenariosResponse(
        scenarios=[GeneratedScenario(**s) for s in scenarios],
        count=len(scenarios)
    )


# ============== LLM Endpoints ==============

@ai_router.post("/llm/query", response_model=QueryTwinResponse)
@handle_ai_errors
async def api_query_twin(request: QueryTwinRequest):
    """
    Ask a natural language question about a digital twin.
    
    Uses LLM to provide intelligent answers about twin state,
    performance, and recommendations.
    """
    answer = query_twin(
        request.question,
        request.twin_data,
        additional_context=request.additional_context
    )
    return QueryTwinResponse(
        answer=answer,
        question=request.question,
        timestamp=datetime.utcnow().isoformat()
    )


@ai_router.post("/llm/insights", response_model=GenerateInsightsResponse)
@handle_ai_errors
async def api_generate_insights(request: GenerateInsightsRequest):
    """
    Generate AI-powered insights about a digital twin.
    
    Analyzes twin data and generates actionable insights
    with recommendations.
    """
    insights = generate_insights(
        request.twin_data,
        focus_areas=request.focus_areas
    )
    return GenerateInsightsResponse(
        insights=[Insight(**i) for i in insights],
        count=len(insights),
        timestamp=datetime.utcnow().isoformat()
    )


@ai_router.post("/llm/explain-anomaly", response_model=ExplainAnomalyResponse)
@handle_ai_errors
async def api_explain_anomaly(request: ExplainAnomalyRequest):
    """
    Get an explanation for an anomaly.
    
    Uses LLM to explain why an anomaly occurred and suggest actions.
    """
    explanation = explain_anomaly(
        request.anomaly,
        request.context
    )
    return ExplainAnomalyResponse(
        explanation=explanation,
        timestamp=datetime.utcnow().isoformat()
    )


# ============== Health Check ==============

@ai_router.get("/health")
async def health_check():
    """Health check endpoint for AI/ML service."""
    return {
        "status": "healthy",
        "service": "ai-ml-layer",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============== Convenience Router ==============

def create_ai_router(prefix: str = "/ai") -> APIRouter:
    """
    Create a configured AI router.
    
    Args:
        prefix: URL prefix for the router
        
    Returns:
        Configured APIRouter instance
        
    Example:
        >>> from ai.api_integration import create_ai_router
        >>> router = create_ai_router(prefix="/api/v1/ai")
        >>> app.include_router(router)
    """
    return ai_router


# ============== Example App ==============

def create_example_app():
    """
    Create an example FastAPI application with AI endpoints.
    
    Returns:
        FastAPI application instance
        
    Example:
        >>> from ai.api_integration import create_example_app
        >>> app = create_example_app()
        >>> # Run with: uvicorn ai.api_integration:create_example_app --factory
    """
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="Digital Twins AI/ML API",
        description="AI and ML capabilities for Digital Twins Platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include AI router
    app.include_router(ai_router, prefix="/api/ai", tags=["AI/ML"])
    
    @app.get("/")
    async def root():
        return {
            "service": "Digital Twins AI/ML API",
            "docs": "/docs",
            "health": "/api/ai/health"
        }
    
    return app
