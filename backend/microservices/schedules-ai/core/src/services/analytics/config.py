"""
Analytics configuration and defaults.

Educational Note:
    Centralizing configuration makes parameter tuning easier
    and allows user-specific overrides without code changes.
"""

import logging
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)


DEFAULT_ANALYTICS_PARAMS = {
    "min_data_points_for_trend": 5,
    "low_sleep_threshold_minutes": 420,
    "low_feedback_threshold": 2.5,
    "consistency_stdev_scale": 2.0,
    "consistency_score_threshold": 0.5,
    "negative_trend_threshold": -5,
}


def initialize_analytics_config(user_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges user configuration with defaults.
    
    Args:
        user_config: User-provided configuration dict
    
    Returns:
        Dict with defaults updated by user values
    
    Educational Note:
        Dictionary update() allows incremental config overrides
        without requiring all parameters to be specified.
    """
    params = DEFAULT_ANALYTICS_PARAMS.copy()
    params.update(user_config.get("analytics_params", {}))
    return params


def extract_thresholds(
    params: Dict[str, Any]
) -> Tuple[int, float, float, int]:
    """
    Extracts threshold values from configuration.
    
    Args:
        params: Configuration dictionary
    
    Returns:
        Tuple of (low_sleep, low_feedback, consistency, trend_threshold)
    
    Educational Note:
        Tuple unpacking simplifies accessing multiple related
        values without repeated dict lookups in caller code.
    """
    low_sleep = params.get("low_sleep_threshold_minutes", 420)
    low_feedback = params.get("low_feedback_threshold", 2.5)
    consistency = params.get("consistency_score_threshold", 0.5)
    trend = params.get("negative_trend_threshold", -5)
    return low_sleep, low_feedback, consistency, trend
