"""
Models module for AI/ML layer.

Contains saved/pretrained models and model utilities.
"""

import os
from pathlib import Path

# Models directory paths
MODELS_DIR = Path(__file__).parent
PRETRAINED_DIR = MODELS_DIR / "pretrained"

# Ensure directories exist
PRETRAINED_DIR.mkdir(parents=True, exist_ok=True)

__all__ = ["MODELS_DIR", "PRETRAINED_DIR"]
