"""
Adaptive Engine (RL) package for parameter optimization.

Provides heuristic-based parameter adaptation with future extensibility
for machine learning models (SFT, RLHF).

Educational Note:
    Package structure separates concerns (models, config, analysis, adaptation)
    making each module independently testable and maintainable.

Usage:
    from src.services.rl import AdaptiveEngineService, AdaptationParameters

    service = AdaptiveEngineService(config={"adaptation_step_size": 0.1})
    adaptations = await service.calculate_adaptations(user_id, trends, feedback)
    updated_params = service.apply_adaptations(current_params, adaptations)
"""

from .models import AdaptationParameters
from .config import DEFAULT_CONFIG
from .service import AdaptiveEngineService

__all__ = [
    "AdaptiveEngineService",
    "AdaptationParameters",
    "DEFAULT_CONFIG",
]
