"""
LLM Interface Module
Natural language interaction with digital twins using LLMs
"""

import os
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


@dataclass
class LLMConfig:
    """Configuration for LLM interface"""
    provider: LLMProvider = LLMProvider.OPENAI
    model: str = "gpt-4o"
    api_key: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    system_prompt: str = ""


# Default configuration
DEFAULT_CONFIG = LLMConfig(
    provider=LLMProvider.OPENAI,
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY"),
    max_tokens=1000,
    temperature=0.7,
)


def query_twin(
    question: str,
    twin_data: Dict[str, Any],
    config: Optional[LLMConfig] = None,
) -> str:
    """
    Answer natural language questions about a digital twin.
    
    Args:
        question: User's question about the twin
        twin_data: Current state and history of the digital twin
        config: LLM configuration
        
    Returns:
        Natural language response
    """
    config = config or DEFAULT_CONFIG
    
    # Build context from twin data
    context = _build_twin_context(twin_data)
    
    # Create prompt
    system_prompt = """You are an expert industrial engineer assistant with deep knowledge of manufacturing equipment, predictive maintenance, and digital twin technology. 

You help operators and engineers understand their equipment by answering questions about digital twins. You provide:
- Clear, concise answers in plain language
- Technical insights when appropriate
- Actionable recommendations
- Safety warnings when relevant

Always base your answers on the provided twin data. If something is uncertain, say so."""

    user_prompt = f"""Twin Data:
{context}

Question: {question}

Please provide a helpful answer based on the twin data above."""

    # Try to call LLM
    try:
        response = _call_llm(system_prompt, user_prompt, config)
        return response
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        # Fallback to rule-based response
        return _generate_fallback_response(question, twin_data)


def generate_insights(
    twin_data: Dict[str, Any],
    config: Optional[LLMConfig] = None,
) -> List[Dict[str, str]]:
    """
    Generate AI-powered insights about a digital twin.
    
    Args:
        twin_data: Current state and history of the digital twin
        config: LLM configuration
        
    Returns:
        List of insights with title, description, and priority
    """
    config = config or DEFAULT_CONFIG
    
    insights = []
    
    # Get sensor data
    sensors = twin_data.get("sensors", [])
    
    # Generate insights based on current state
    for sensor in sensors:
        sensor_name = sensor.get("name", sensor.get("id", "Unknown"))
        value = sensor.get("current_value", sensor.get("value"))
        warning = sensor.get("warning_threshold")
        critical = sensor.get("critical_threshold")
        
        if critical and value and value > critical * 0.9:
            insights.append({
                "title": f"Critical: {sensor_name}",
                "description": f"{sensor_name} is at {value}, approaching critical threshold of {critical}",
                "priority": "critical",
                "category": "alert",
                "recommendation": f"Immediate attention required for {sensor_name}",
            })
        elif warning and value and value > warning * 0.8:
            insights.append({
                "title": f"Warning: {sensor_name}",
                "description": f"{sensor_name} is at {value}, elevated above normal range",
                "priority": "warning",
                "category": "monitoring",
                "recommendation": f"Monitor {sensor_name} closely and plan maintenance",
            })
    
    # Operating hours insight
    hours = twin_data.get("operating_hours") or twin_data.get("metadata", {}).get("operating_hours")
    if hours and hours > 20000:
        insights.append({
            "title": "High Operating Hours",
            "description": f"Equipment has {hours:,.0f} operating hours. Consider scheduling comprehensive maintenance.",
            "priority": "info",
            "category": "maintenance",
            "recommendation": "Schedule preventive maintenance inspection",
        })
    
    # Efficiency insights
    load = next((s for s in sensors if "load" in s.get("name", "").lower()), None)
    if load:
        load_val = load.get("current_value", load.get("value", 0))
        if load_val < 40:
            insights.append({
                "title": "Low Utilization",
                "description": f"Current load is only {load_val}%. Equipment may be underutilized.",
                "priority": "info",
                "category": "optimization",
                "recommendation": "Consider consolidating workload or adjusting production schedule",
            })
    
    # Try to enhance with LLM if available
    if config.api_key:
        try:
            llm_insights = _generate_llm_insights(twin_data, config)
            insights.extend(llm_insights)
        except Exception as e:
            logger.warning(f"LLM insight generation failed: {e}")
    
    # Sort by priority
    priority_order = {"critical": 0, "warning": 1, "info": 2}
    insights.sort(key=lambda x: priority_order.get(x.get("priority", "info"), 2))
    
    return insights[:10]  # Return top 10


def explain_anomaly(
    anomaly: Dict[str, Any],
    context: Dict[str, Any],
    config: Optional[LLMConfig] = None,
) -> str:
    """
    Explain why an anomaly occurred in natural language.
    
    Args:
        anomaly: Anomaly details
        context: Additional context (twin data, history, etc.)
        config: LLM configuration
        
    Returns:
        Natural language explanation
    """
    config = config or DEFAULT_CONFIG
    
    sensor_name = anomaly.get("sensor_name", anomaly.get("name", "Unknown sensor"))
    value = anomaly.get("value", 0)
    anomaly_type = anomaly.get("anomaly_type", "unknown")
    severity = anomaly.get("severity", "unknown")
    
    # Build explanation based on anomaly type
    explanations = {
        "spike": f"The {sensor_name} experienced a sudden spike to {value}. This could indicate a sudden load change, process upset, or sensor malfunction.",
        "drop": f"The {sensor_name} dropped unexpectedly to {value}. This may indicate a loss of flow, pressure, or equipment issue.",
        "drift": f"The {sensor_name} has been gradually drifting from normal values. This often indicates progressive wear or calibration shift.",
        "oscillation": f"The {sensor_name} is showing unusual oscillation patterns. This could indicate control loop issues or mechanical instability.",
        "out_of_range": f"The {sensor_name} reading of {value} is outside the valid operating range, suggesting a sensor or process issue.",
    }
    
    base_explanation = explanations.get(
        anomaly_type,
        f"An anomaly was detected in {sensor_name} with value {value}."
    )
    
    # Add severity context
    severity_context = {
        "critical": " This requires immediate attention.",
        "warning": " This should be investigated soon.",
        "info": " This is for informational purposes.",
    }
    base_explanation += severity_context.get(severity, "")
    
    # Add possible causes
    causes = anomaly.get("possible_causes", [])
    if causes:
        base_explanation += f"\n\nPossible causes:\n"
        for cause in causes[:3]:
            base_explanation += f"• {cause}\n"
    
    # Try LLM enhancement
    if config.api_key:
        try:
            context_str = json.dumps(context, indent=2, default=str)[:2000]
            prompt = f"""Anomaly detected:
{json.dumps(anomaly, indent=2, default=str)}

Context:
{context_str}

Provide a clear, concise explanation for an operator about why this anomaly might have occurred and what to check first. Keep it under 100 words."""
            
            llm_explanation = _call_llm(
                "You are an expert industrial equipment diagnostician.",
                prompt,
                config,
            )
            if llm_explanation:
                return llm_explanation
        except Exception as e:
            logger.warning(f"LLM explanation failed: {e}")
    
    return base_explanation


# Private helper functions

def _build_twin_context(twin_data: Dict[str, Any]) -> str:
    """Build a text context from twin data for LLM"""
    parts = []
    
    # Basic info
    name = twin_data.get("name", "Unknown Equipment")
    twin_type = twin_data.get("type", "Unknown")
    status = twin_data.get("status", "Unknown")
    
    parts.append(f"Equipment: {name}")
    parts.append(f"Type: {twin_type}")
    parts.append(f"Status: {status}")
    
    # Location
    location = twin_data.get("location", {})
    if location:
        loc_str = f"Location: {location.get('building', '')} - {location.get('area', '')}"
        parts.append(loc_str)
    
    # Sensors
    sensors = twin_data.get("sensors", [])
    if sensors:
        parts.append("\nCurrent Sensor Readings:")
        for sensor in sensors[:10]:  # Limit to 10 sensors
            sensor_name = sensor.get("name", sensor.get("id", "Unknown"))
            value = sensor.get("current_value", sensor.get("value", "N/A"))
            unit = sensor.get("unit", "")
            warning = sensor.get("warning_threshold")
            critical = sensor.get("critical_threshold")
            
            line = f"  - {sensor_name}: {value}{unit}"
            if critical and value > critical:
                line += " [CRITICAL]"
            elif warning and value > warning:
                line += " [WARNING]"
            parts.append(line)
    
    # Metadata
    metadata = twin_data.get("metadata", {})
    if metadata:
        parts.append("\nEquipment Info:")
        if "manufacturer" in metadata:
            parts.append(f"  Manufacturer: {metadata['manufacturer']}")
        if "model" in metadata:
            parts.append(f"  Model: {metadata['model']}")
        if "last_maintenance" in metadata:
            parts.append(f"  Last Maintenance: {metadata['last_maintenance']}")
    
    return "\n".join(parts)


def _call_llm(system_prompt: str, user_prompt: str, config: LLMConfig) -> str:
    """Make API call to LLM provider"""
    if not config.api_key:
        raise ValueError("No API key configured")
    
    if config.provider == LLMProvider.OPENAI:
        return _call_openai(system_prompt, user_prompt, config)
    elif config.provider == LLMProvider.ANTHROPIC:
        return _call_anthropic(system_prompt, user_prompt, config)
    else:
        raise ValueError(f"Unsupported provider: {config.provider}")


def _call_openai(system_prompt: str, user_prompt: str, config: LLMConfig) -> str:
    """Call OpenAI API"""
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")
    
    client = openai.OpenAI(api_key=config.api_key)
    
    response = client.chat.completions.create(
        model=config.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=config.max_tokens,
        temperature=config.temperature,
    )
    
    return response.choices[0].message.content


def _call_anthropic(system_prompt: str, user_prompt: str, config: LLMConfig) -> str:
    """Call Anthropic API"""
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")
    
    client = anthropic.Anthropic(api_key=config.api_key)
    
    response = client.messages.create(
        model=config.model or "claude-3-sonnet-20240229",
        max_tokens=config.max_tokens,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_prompt},
        ],
    )
    
    return response.content[0].text


def _generate_fallback_response(question: str, twin_data: Dict[str, Any]) -> str:
    """Generate a response without LLM using rules"""
    question_lower = question.lower()
    
    # Status questions
    if "status" in question_lower or "how is" in question_lower:
        status = twin_data.get("status", "unknown")
        return f"The equipment status is currently: {status}."
    
    # Temperature questions
    if "temp" in question_lower or "hot" in question_lower:
        sensors = twin_data.get("sensors", [])
        temp_sensor = next((s for s in sensors if "temp" in s.get("name", "").lower()), None)
        if temp_sensor:
            value = temp_sensor.get("current_value", temp_sensor.get("value", "unknown"))
            unit = temp_sensor.get("unit", "°C")
            return f"The current temperature is {value}{unit}."
        return "No temperature sensor data available."
    
    # Load questions
    if "load" in question_lower or "capacity" in question_lower:
        sensors = twin_data.get("sensors", [])
        load_sensor = next((s for s in sensors if "load" in s.get("name", "").lower()), None)
        if load_sensor:
            value = load_sensor.get("current_value", load_sensor.get("value", "unknown"))
            return f"The current load is {value}%."
        return "No load sensor data available."
    
    # Maintenance questions
    if "maintenance" in question_lower or "service" in question_lower:
        metadata = twin_data.get("metadata", {})
        last_maint = metadata.get("last_maintenance", "unknown")
        return f"The last maintenance was performed on {last_maint}."
    
    # Generic response
    return f"I don't have a specific answer for that question. The equipment ({twin_data.get('name', 'Unknown')}) is currently {twin_data.get('status', 'in unknown state')}."


def _generate_llm_insights(twin_data: Dict[str, Any], config: LLMConfig) -> List[Dict[str, str]]:
    """Generate additional insights using LLM"""
    context = _build_twin_context(twin_data)
    
    prompt = f"""Based on this digital twin data, generate 2-3 actionable insights for an operator:

{context}

Format each insight as JSON:
{{"title": "...", "description": "...", "priority": "info|warning|critical", "category": "maintenance|optimization|alert", "recommendation": "..."}}

Return only a JSON array of insights."""

    try:
        response = _call_llm(
            "You are an industrial equipment expert. Generate concise, actionable insights.",
            prompt,
            config,
        )
        
        # Parse JSON from response
        # Handle potential markdown code blocks
        if "```" in response:
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        
        insights = json.loads(response)
        return insights if isinstance(insights, list) else [insights]
        
    except Exception as e:
        logger.warning(f"Failed to parse LLM insights: {e}")
        return []
