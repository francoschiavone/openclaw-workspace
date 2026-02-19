"""
Configuration management for the Digital Twins Platform
"""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Ditto API configuration
    ditto_api_url: str = "http://localhost:8080"
    ditto_ws_url: str = "ws://localhost:8081"
    ditto_devops_user: str = "devops"
    ditto_devops_password: str = "dittoPwd"

    # MQTT configuration
    mqtt_broker_url: str = "mqtt://localhost:1883"
    mqtt_client_id: str = "digital-twins-backend"

    # Application settings
    app_name: str = "Digital Twins Platform"
    debug: bool = False
    log_level: str = "INFO"

    # API settings
    api_prefix: str = "/api/v1"

    model_config = {"env_file": ".env", "case_sensitive": False}


# Global settings instance
settings = Settings()
