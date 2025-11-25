"""
Data structures for sleep analysis and recommendations.

This module defines the core data containers used throughout the sleep
package, including sleep metrics and fallback enumerations for external
dependencies.

Educational Note:
    Using frozen dataclasses for immutable sleep metrics prevents
    accidental modification of calculated values and ensures thread-safe
    access in async contexts.
"""

from dataclasses import dataclass, field
from datetime import time, timedelta
from enum import Enum
from typing import Optional


def _format_timedelta(delta: Optional[timedelta]) -> str:
    """
    Format a timedelta into human-readable hours and minutes.

    Args:
        delta: The timedelta to format, or None

    Returns:
        str: Formatted string like "8h 30m" or "N/A"

    Educational Note:
        Provides consistent formatting across all sleep duration displays,
        improving user experience and debugging clarity.
    """
    if delta is None:
        return "N/A"
    total_seconds = int(delta.total_seconds())
    sign = "-" if total_seconds < 0 else ""
    total_seconds = abs(total_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    if hours > 0:
        return f"{sign}{hours}h {minutes}m"
    return f"{sign}{minutes}m"


class SleepNeed(Enum):
    """
    Sleep need category based on cycle count adjustment.

    Educational Note:
        LOW: base - 1 cycle (less sleep needed)
        MEDIUM: base cycles (average sleep)
        HIGH: base + 1 cycle (more sleep needed)
        
        Teens (<18): 50min cycles, base 11 → LOW=10, MED=11, HIGH=12
        Adults (≥18): 90min cycles, base 5 → LOW=4, MED=5, HIGH=6
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Chronotype(Enum):
    """
    Fallback chronotype enumeration if external module unavailable.

    Educational Note:
        Provides graceful degradation when chronotype analysis module
        is not imported, preventing hard dependencies between modules.
    """
    EARLY_BIRD = "early_bird"
    NIGHT_OWL = "night_owl"
    INTERMEDIATE = "intermediate"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class SleepMetrics:
    """
    Immutable container for sleep measurements and recommendations.

    This dataclass stores both ideal (recommended) and actual sleep
    parameters, enabling comparison and quality assessment.

    Attributes:
        ideal_duration: Recommended total sleep duration
        ideal_bedtime: Recommended time to go to bed (local time)
        ideal_wake_time: Recommended time to wake up (local time)
        actual_duration: Actual total sleep duration from data (if available)
        actual_bedtime: Actual bedtime from data (local time, if available)
        actual_wake_time: Actual wake time from data (local time, if available)
        sleep_quality_score: Overall sleep quality score 0-100 (if calculated)
        sleep_deficit: Difference between ideal and actual duration (computed)

    Educational Note:
        Frozen dataclasses are immutable after creation, which prevents
        bugs from unintended state mutations and makes the objects safe
        to use in async contexts without locking.
    """
    ideal_duration: timedelta
    ideal_bedtime: time
    ideal_wake_time: time

    actual_duration: Optional[timedelta] = None
    actual_bedtime: Optional[time] = None
    actual_wake_time: Optional[time] = None
    sleep_quality_score: Optional[float] = None

    sleep_deficit: Optional[timedelta] = field(init=False, default=None)

    def __post_init__(self):
        """
        Compute derived field (sleep_deficit) after initialization.

        Educational Note:
            __post_init__ in dataclasses allows computed fields to be set
            even when the dataclass is frozen, by using object.__setattr__
            during the initialization phase.
        """
        if self.actual_duration is not None:
            deficit = self.ideal_duration - self.actual_duration
            object.__setattr__(self, 'sleep_deficit', deficit)

    def __str__(self) -> str:
        """
        Generate human-readable string representation.

        Educational Note:
            Custom __str__ methods improve debugging and logging by
            providing context-specific formatted output rather than
            default object representations.
        """
        rec_dur_str = _format_timedelta(self.ideal_duration)
        act_dur_str = _format_timedelta(self.actual_duration)
        deficit_str = _format_timedelta(self.sleep_deficit)
        score_str = (
            f"{self.sleep_quality_score:.1f}"
            if self.sleep_quality_score is not None
            else "N/A"
        )
        bed_act = (
            self.actual_bedtime.strftime('%H:%M')
            if self.actual_bedtime
            else 'N/A'
        )
        wake_act = (
            self.actual_wake_time.strftime('%H:%M')
            if self.actual_wake_time
            else 'N/A'
        )

        ideal_bed_str = self.ideal_bedtime.strftime('%H:%M')
        ideal_wake_str = self.ideal_wake_time.strftime('%H:%M')

        return (
            f"SleepMetrics(Ideal: {ideal_bed_str}-{ideal_wake_str} "
            f"[{rec_dur_str}], Actual: {bed_act}-{wake_act} "
            f"[{act_dur_str}], Deficit: {deficit_str}, "
            f"Score: {score_str}/100)"
        )
