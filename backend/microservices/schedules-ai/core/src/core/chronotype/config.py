"""
Chronotype configuration constants.

This module defines MEQ score ranges and prime productive windows
for each chronotype.

Educational Note:
    Simple configuration maps MEQ scores to chronotypes and defines
    optimal 3-5 hour productive windows based on circadian research.
"""

from datetime import time
from typing import Dict, Tuple

from src.core.chronotype.models import Chronotype, PrimeWindow


MEQ_RANGES: Dict[Tuple[int, int], Chronotype] = {
    (16, 41): Chronotype.NIGHT_OWL,
    (42, 58): Chronotype.INTERMEDIATE,
    (59, 86): Chronotype.EARLY_BIRD,
}


PRIME_WINDOWS: Dict[Chronotype, PrimeWindow] = {
    Chronotype.EARLY_BIRD: PrimeWindow(
        start=time(7, 0),
        end=time(11, 0),
        chronotype=Chronotype.EARLY_BIRD
    ),
    Chronotype.INTERMEDIATE: PrimeWindow(
        start=time(10, 0),
        end=time(16, 0),
        chronotype=Chronotype.INTERMEDIATE
    ),
    Chronotype.NIGHT_OWL: PrimeWindow(
        start=time(17, 0),
        end=time(22, 0),
        chronotype=Chronotype.NIGHT_OWL
    ),
    Chronotype.UNKNOWN: PrimeWindow(
        start=time(10, 0),
        end=time(14, 0),
        chronotype=Chronotype.UNKNOWN
    ),
}
