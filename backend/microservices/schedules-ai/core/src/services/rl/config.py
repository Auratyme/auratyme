"""
Configuration management for adaptive engine service.

Provides default configuration and initialization utilities.

Educational Note:
    Centralized config with defaults ensures consistent behavior across
    environments while allowing easy customization per deployment.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    "adaptation_step_size": 0.05,
    "min_data_points_for_trend": 5,
    "low_feedback_threshold": 2.5,
    "high_sleep_deficit_threshold_minutes": 45,
    "low_sleep_threshold_minutes": 420,
    "negative_trend_threshold": -5,
}


def initialize_config(user_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges user config with defaults.
    
    Educational Note:
        Config merge pattern allows partial overrides without requiring
        users to specify every parameter, reducing configuration burden.
    """
    config = DEFAULT_CONFIG.copy()
    if user_config:
        config.update(user_config)
    return config


def extract_config_values(config: Dict[str, Any]) -> tuple:
    """
    Extracts commonly used config values into tuple for easy access.
    
    Educational Note:
        Unpacking config into named variables improves code readability
        and makes parameter usage explicit throughout service.
    """
    return (
        config["adaptation_step_size"],
        config["min_data_points_for_trend"],
        config["low_feedback_threshold"],
        config["high_sleep_deficit_threshold_minutes"],
    )
