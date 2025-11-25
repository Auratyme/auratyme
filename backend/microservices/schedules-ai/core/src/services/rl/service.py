"""
Adaptive Engine Service main class.

Coordinates parameter adaptation based on historical performance and feedback.

Educational Note:
    Service layer pattern isolates business logic from infrastructure,
    making it easy to test adaptation algorithms without full system setup.
"""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from .models import AdaptationParameters
from .config import DEFAULT_CONFIG, initialize_config, extract_config_values
from .analyzer import calculate_adaptations as calc_adapt
from .adapter import apply_adaptations as apply_adapt

logger = logging.getLogger(__name__)


class AdaptiveEngineService:
    """
    Manages scheduling parameter adaptation using heuristics or ML models.
    
    Educational Note:
        Service class coordinates multiple specialized modules (config,
        analyzer, adapter) following single responsibility principle.
    """
    
    DEFAULT_CONFIG = DEFAULT_CONFIG
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initializes adaptive engine with configuration.
        
        Educational Note:
            Config merge pattern allows easy testing with overrides
            while maintaining production defaults for robustness.
        """
        self._config = initialize_config(config or {})
        
        values = extract_config_values(self._config)
        self._adaptation_step = values[0]
        self._min_data_points = values[1]
        self._low_feedback_thr = values[2]
        self._high_deficit_thr = values[3]
        
        self._adaptation_policy_model = None
        
        logger.info("AdaptiveEngineService initialized")
        logger.debug(f"Config: {self._config}")
    
    async def calculate_adaptations(
        self,
        user_id: UUID,
        trend_analysis: Optional[Any] = None,
        recent_feedback_analysis: Optional[Any] = None,
    ) -> AdaptationParameters:
        """
        Calculates parameter adaptations from analysis results.
        
        Educational Note:
            Async method signature enables future ML model inference
            that might require network calls or heavy computation.
        """
        return calc_adapt(
            user_id=user_id,
            trend_analysis=trend_analysis,
            feedback_analysis=recent_feedback_analysis,
            config=self._config,
            adaptation_step=self._adaptation_step,
            low_feedback_thr=self._low_feedback_thr
        )
    
    def apply_adaptations(
        self,
        current_params: Dict[str, Any],
        adaptations: AdaptationParameters
    ) -> Dict[str, Any]:
        """
        Applies calculated adaptations to parameter dictionary.
        
        Educational Note:
            Synchronous application enables immediate parameter updates
            without async complexity when no I/O needed.
        """
        return apply_adapt(current_params, adaptations)
