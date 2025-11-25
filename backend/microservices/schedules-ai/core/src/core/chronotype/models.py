"""
Chronotype data models.

This module defines core data structures for chronotype representation,
including the chronotype classification enum and simplified profile.

Educational Note:
    Simplified model focuses on core functionality:
    1. MEQ score → Chronotype classification
    2. Chronotype → Prime productive window (3-5h)
"""

from dataclasses import dataclass
from datetime import time
from enum import Enum
from typing import Tuple


class Chronotype(Enum):
    """
    User chronotype classification based on MEQ questionnaire.

    Educational Note:
        Three main chronotypes based on circadian preference:
        - EARLY_BIRD: Peak energy in morning (MEQ 59-86)
        - INTERMEDIATE: Flexible, peak mid-day (MEQ 42-58)
        - NIGHT_OWL: Peak energy in evening (MEQ 16-41)
        - UNKNOWN: When MEQ data unavailable
    """
    EARLY_BIRD = "early_bird"
    INTERMEDIATE = "intermediate"
    NIGHT_OWL = "night_owl"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PrimeWindow:
    """
    Prime productive window for a chronotype.

    Educational Note:
        Prime window represents the 3-5 hour period when user
        has peak cognitive performance and energy based on
        their circadian rhythm.
    """
    start: time
    end: time
    chronotype: Chronotype

    def duration_hours(self) -> float:
        """
        Calculate window duration in hours.

        Returns:
            float: Duration in hours

        Educational Note:
            Simple duration calculation for validation and display.
        """
        start_minutes = self.start.hour * 60 + self.start.minute
        end_minutes = self.end.hour * 60 + self.end.minute
        return (end_minutes - start_minutes) / 60.0
