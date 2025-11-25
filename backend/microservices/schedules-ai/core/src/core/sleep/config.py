"""
Sleep configuration constants and defaults.

This module centralizes all configurable parameters for sleep calculation,
quality analysis, and recommendation generation.

Educational Note:
    Centralizing configuration in a dedicated module makes the system
    more maintainable and testable. Users can override specific values
    without touching business logic code.
"""

from datetime import time
from typing import Any, Dict, Tuple

from src.core.chronotype.models import Chronotype
from src.core.sleep.models import SleepNeed


TEEN_CYCLE_MINUTES: int = 50
ADULT_CYCLE_MINUTES: int = 90

TEEN_BASE_CYCLES: int = 11
ADULT_BASE_CYCLES: int = 5

SLEEP_NEED_CYCLE_ADJUSTMENTS: Dict[SleepNeed, int] = {
    SleepNeed.LOW: -1,
    SleepNeed.MEDIUM: 0,
    SleepNeed.HIGH: +1,
}

AGE_CHRONOTYPE_TIMING_SHIFTS: Dict[str, Dict[Chronotype, float]] = {
    "teen": {
        Chronotype.EARLY_BIRD: 0.0,
        Chronotype.INTERMEDIATE: +0.5,
        Chronotype.NIGHT_OWL: +2.0,
        Chronotype.UNKNOWN: +0.5,
    },
    "adult": {
        Chronotype.EARLY_BIRD: 0.0,
        Chronotype.INTERMEDIATE: +0.5,
        Chronotype.NIGHT_OWL: +1.5,
        Chronotype.UNKNOWN: +0.5,
    },
    "senior": {
        Chronotype.EARLY_BIRD: -0.5,
        Chronotype.INTERMEDIATE: 0.0,
        Chronotype.NIGHT_OWL: +1.0,
        Chronotype.UNKNOWN: 0.0,
    },
}

SLEEP_ONSET_MINUTES: int = 15

DEFAULT_WAKE_TIMES: Dict[Chronotype, time] = {
    Chronotype.EARLY_BIRD: time(6, 0),
    Chronotype.INTERMEDIATE: time(7, 30),
    Chronotype.NIGHT_OWL: time(9, 0),
    Chronotype.UNKNOWN: time(7, 30),
}


DEFAULT_SLEEP_CONFIG: Dict[str, Any] = {
    "teen_cycle_minutes": TEEN_CYCLE_MINUTES,
    "adult_cycle_minutes": ADULT_CYCLE_MINUTES,
    "teen_base_cycles": TEEN_BASE_CYCLES,
    "adult_base_cycles": ADULT_BASE_CYCLES,
    "sleep_need_cycle_adjustments": SLEEP_NEED_CYCLE_ADJUSTMENTS,
    "age_chronotype_timing_shifts": AGE_CHRONOTYPE_TIMING_SHIFTS,
    "default_wake_times": DEFAULT_WAKE_TIMES,
    "sleep_onset_minutes": SLEEP_ONSET_MINUTES,
}
