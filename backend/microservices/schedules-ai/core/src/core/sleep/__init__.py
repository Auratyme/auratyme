"""
Sleep analysis package initialization.

This module provides a unified interface to the sleep analysis functionality
through the SleepCalculator class, which coordinates all sleep-related
calculations and analyses.

Educational Note:
    Package initialization modules provide clean public APIs while hiding
    internal implementation details. This allows refactoring without
    breaking user code.
"""

import logging
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.core.sleep.config import DEFAULT_SLEEP_CONFIG
from src.core.sleep.guidelines import get_recommended_sleep_duration
from src.core.chronotype.models import Chronotype
from src.core.sleep.models import SleepMetrics, SleepNeed
from src.core.sleep.quality import analyze_sleep_quality
from src.core.sleep.windows import (
    calculate_sleep_window,
    suggest_wake_times_based_on_cycles,
)

logger = logging.getLogger(__name__)


class SleepCalculator:
    """
    Facade class for sleep calculation and analysis.

    This class provides a simple interface to all sleep-related
    functionality while managing configuration internally.

    Educational Note:
        Facade pattern simplifies complex subsystems by providing
        a unified interface that handles configuration distribution
        and coordinates multiple internal modules.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize sleep calculator with configuration.

        Args:
            config: Configuration overrides for defaults

        Educational Note:
            Constructor merges user config with defaults, allowing
            customization while ensuring all required values exist.
        """
        self._config = DEFAULT_SLEEP_CONFIG.copy()
        if config:
            self._config.update(config)

        logger.info("SleepCalculator initialized")

    def get_recommended_sleep_duration(
        self,
        age: int,
        sleep_need: SleepNeed
    ) -> timedelta:
        """
        Calculate sleep duration from age and sleep cycles.

        Args:
            age: User's age (determines cycle length and base)
            sleep_need: LOW/MEDIUM/HIGH (±1 cycle)

        Returns:
            timedelta: Sleep duration

        Educational Note:
            Teens (<18): 50min cycles × (10/11/12)
            Adults (≥18): 90min cycles × (4/5/6)
        """
        return get_recommended_sleep_duration(
            age,
            sleep_need,
            self._config["teen_cycle_minutes"],
            self._config["adult_cycle_minutes"],
            self._config["teen_base_cycles"],
            self._config["adult_base_cycles"],
            self._config["sleep_need_cycle_adjustments"]
        )

    def calculate_sleep_window(
        self,
        age: int,
        chronotype: Chronotype,
        sleep_need: SleepNeed,
        target_wake_time: Optional[time] = None
    ) -> SleepMetrics:
        """
        Calculate sleep window with sleep onset compensation.

        Args:
            age: User's age (base duration)
            chronotype: EARLY_BIRD/INTERMEDIATE/NIGHT_OWL (timing)
            sleep_need: LOW/MEDIUM/HIGH (adjustment)
            target_wake_time: Optional preferred wake time

        Returns:
            SleepMetrics: Complete sleep window

        Educational Note:
            THREE inputs + sleep onset (15min to fall asleep):
            1. Age + sleep_need → duration
            2. Chronotype → timing shift
            3. Sleep onset → bedtime 15min earlier
        """
        sleep_duration = self.get_recommended_sleep_duration(age, sleep_need)
        sleep_onset = timedelta(minutes=self._config["sleep_onset_minutes"])
        
        total_time_in_bed = sleep_duration + sleep_onset

        return calculate_sleep_window(
            age,
            chronotype,
            total_time_in_bed,
            target_wake_time,
            self._config["default_wake_times"],
            self._config["age_chronotype_timing_shifts"],
            sleep_onset
        )

    def suggest_wake_times_based_on_cycles(
        self,
        bedtime: time,
        min_cycles: int = 4,
        max_cycles: int = 6
    ) -> List[time]:
        """
        Suggest optimal wake times for completing full sleep cycles.

        Args:
            bedtime: Intended bedtime
            min_cycles: Minimum cycles to suggest (default: 4)
            max_cycles: Maximum cycles to suggest (default: 6)

        Returns:
            List[time]: Sorted list of suggested wake times

        Educational Note:
            Provides user-friendly sleep cycle optimization without
            requiring detailed sleep science knowledge.
        """
        return suggest_wake_times_based_on_cycles(
            bedtime,
            self._sleep_onset_minutes,
            self._sleep_cycle_duration_minutes,
            min_cycles,
            max_cycles
        )

    def analyze_sleep_quality(
        self,
        recommended: SleepMetrics,
        sleep_start: datetime,
        sleep_end: datetime,
        heart_rate_data: Optional[List[Tuple[datetime, int]]] = None,
        hrv_data: Optional[List[Tuple[datetime, float]]] = None,
    ) -> SleepMetrics:
        """
        Analyze sleep quality against recommendations.

        Args:
            recommended: Recommended sleep metrics
            sleep_start: Actual sleep start (timezone-aware)
            sleep_end: Actual sleep end (timezone-aware)
            heart_rate_data: List of (datetime, bpm) tuples
            hrv_data: List of (datetime, rmssd_ms) tuples

        Returns:
            SleepMetrics: Updated metrics with quality score

        Raises:
            ValueError: If inputs are invalid

        Educational Note:
            Orchestrates complete quality analysis while hiding
            complex parameter passing and coordination logic.
        """
        return analyze_sleep_quality(
            recommended,
            sleep_start,
            sleep_end,
            heart_rate_data,
            hrv_data,
            self._duration_tolerance,
            self._duration_penalty_range,
            self._timing_tolerance,
            self._timing_penalty_range,
            self._hr_target_min,
            self._hr_target_max,
            self._hr_penalty_low,
            self._hr_penalty_high,
            self._hrv_target,
            self._hrv_scale,
            self._physio_weights,
            self._quality_weights
        )


__all__ = [
    "SleepCalculator",
    "SleepMetrics",
    "Chronotype",
]
