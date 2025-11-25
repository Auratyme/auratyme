"""
Configuration for wearable service sleep window detection.

Defines time windows for identifying primary sleep sessions.

Educational Note:
    Configurable sleep windows adapt to different lifestyles
    (night shift workers, early risers) without code changes.
"""

import logging
from typing import Any, Dict
from datetime import time

logger = logging.getLogger(__name__)

DEFAULT_SLEEP_WINDOW_START_HOUR = 0
DEFAULT_SLEEP_WINDOW_END_HOUR = 14


def get_sleep_window_hours(config: Dict[str, Any]) -> tuple[int, int]:
    """
    Extracts sleep window hours from config.
    
    Educational Note:
        Centralized config extraction with validation ensures
        consistent behavior across service instances.
    """
    start_hour = config.get(
        "primary_sleep_end_window_start_hour",
        DEFAULT_SLEEP_WINDOW_START_HOUR
    )
    end_hour = config.get(
        "primary_sleep_end_window_end_hour",
        DEFAULT_SLEEP_WINDOW_END_HOUR
    )
    
    return start_hour, end_hour


def create_sleep_window_times(start_hour: int, end_hour: int) -> tuple:
    """
    Creates time objects for sleep window boundaries.
    
    Educational Note:
        Exception handling with fallback ensures service
        continues operating even with invalid configuration.
    """
    try:
        window_start = time(start_hour, 0)
        window_end = time(end_hour, 0)
        return window_start, window_end
    except ValueError:
        logger.error(
            f"Invalid sleep window hours: {start_hour}-{end_hour}, "
            "using defaults 00:00-14:00"
        )
        return time(0, 0), time(14, 0)
