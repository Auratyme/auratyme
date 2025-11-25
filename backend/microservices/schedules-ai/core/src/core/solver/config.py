"""
Solver Configuration Management.

Handles extraction and validation of solver configuration parameters
including time limits, objective weights, and other solver settings.

Educational Context:
    Configuration management is separated to keep the main solver class
    focused on orchestration. This module handles the messy details of
    extracting, validating, and providing defaults for configuration values.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def extract_time_limit(config: Dict[str, Any]) -> float:
    """
    Extracts solver time limit from configuration.

    Returns:
        Time limit in seconds (default: 30.0)

    Educational Note:
        Default values provide sensible behavior when config is incomplete.
        This defensive programming prevents crashes from missing config.
    """
    return float(config.get("solver_time_limit_seconds", 30.0))


def get_default_weights() -> Dict[str, int]:
    """
    Provides default objective function weights.

    Educational Note:
        Energy matching (50) is critical for chronotype-aligned scheduling.
        High weight ensures tasks schedule during peak energy windows.
        Priority (10) differentiates task importance. Start penalty (1)
        provides tiebreaker for equally good time slots.
        
        Weight scaling:
        - High energy task (level 3): 50 * 3 * 100 = 15,000 max contribution
        - Medium energy task (level 2): 50 * 2 * 100 = 10,000 max contribution
        - Low energy task (level 1): 50 * 1 * 100 = 5,000 max contribution
        
        This ensures energy matching dominates start_time_penalty (max 1,440)
        for proper chronotype alignment.
    """
    return {
        "priority": 10,
        "energy_match": 50,
        "start_time_penalty": 1
    }


def extract_user_weights(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts user-provided objective weights from config.

    Educational Note:
        We separate extraction from merging to make the code testable.
        This function just retrieves the weights, another handles merging.
    """
    return config.get("objective_weights", {})


def is_valid_weight_value(value: Any) -> bool:
    """
    Checks if a weight value is numeric.

    Educational Note:
        Type checking prevents runtime errors from invalid configuration.
        We only accept int or float, rejecting strings, None, etc.
    """
    return isinstance(value, (int, float))


def filter_valid_weights(user_weights: Dict[str, Any]) -> Dict[str, int]:
    """
    Filters out non-numeric weight values.

    Educational Note:
        Rather than crash on bad config, we skip invalid values and log
        a warning. This makes the system more robust to config errors.
    """
    valid_weights = {}
    
    for key, value in user_weights.items():
        if is_valid_weight_value(value):
            valid_weights[key] = int(value)
        else:
            logger.warning(f"Ignoring invalid weight '{key}': {value}")
    
    return valid_weights


def merge_weights(
    defaults: Dict[str, int],
    user_weights: Dict[str, int]
) -> Dict[str, int]:
    """
    Merges user weights with defaults.

    Educational Note:
        We start with defaults, then override with user values. This lets
        users customize specific weights while keeping others at defaults.
    """
    merged = defaults.copy()
    merged.update(user_weights)
    return merged


def extract_objective_weights(config: Dict[str, Any]) -> Dict[str, int]:
    """
    Extracts and validates objective function weights.

    Returns:
        Dictionary of weight names to integer values

    Educational Note:
        This orchestrates the entire weight extraction pipeline: get defaults,
        extract user values, validate them, and merge. Each step is a small,
        testable function.
    """
    defaults = get_default_weights()
    user_weights = extract_user_weights(config)
    valid_weights = filter_valid_weights(user_weights)
    return merge_weights(defaults, valid_weights)


def log_configuration(time_limit: float, weights: Dict[str, int]) -> None:
    """
    Logs solver configuration for debugging.

    Educational Note:
        Logging configuration helps diagnose issues. If results seem wrong,
        first check if the configuration matches expectations.
    """
    logger.info(f"Solver config: limit={time_limit}s, weights={weights}")
