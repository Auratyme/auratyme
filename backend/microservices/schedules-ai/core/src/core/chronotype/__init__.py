"""
Chronotype analysis package - simplified interface.

This module provides simple MEQ to Chronotype conversion with
prime productive windows.

Educational Note:
    Simplified chronotype system:
    1. MEQ score (16-86) → Chronotype classification
    2. Chronotype → Prime window (3-5h peak performance)
"""

import logging
from typing import Optional

from src.core.chronotype.classifier import determine_chronotype_from_meq
from src.core.chronotype.config import MEQ_RANGES, PRIME_WINDOWS
from src.core.chronotype.models import Chronotype, PrimeWindow

logger = logging.getLogger(__name__)


class ChronotypeAnalyzer:
    """
    Simple chronotype analyzer: MEQ → Chronotype → Prime Window.

    Educational Note:
        Focused facade providing only essential functionality:
        - MEQ score classification
        - Prime window retrieval
    """

    def __init__(self) -> None:
        """
        Initialize chronotype analyzer with default configuration.

        Educational Note:
            No complex configuration needed - uses research-based
            MEQ ranges and prime windows directly.
        """
        logger.info("ChronotypeAnalyzer initialized (simplified)")

    def determine_chronotype_from_meq(self, meq_score: int) -> Chronotype:
        """
        Determine chronotype from MEQ questionnaire score.

        Args:
            meq_score: MEQ score (16-86)

        Returns:
            Chronotype: EARLY_BIRD, INTERMEDIATE, or NIGHT_OWL

        Raises:
            ValueError: If MEQ score is invalid

        Educational Note:
            Maps MEQ scores to chronotypes:
            - 16-41: NIGHT_OWL
            - 42-58: INTERMEDIATE
            - 59-86: EARLY_BIRD
        """
        return determine_chronotype_from_meq(meq_score, MEQ_RANGES)

    def get_prime_window(self, chronotype: Chronotype) -> PrimeWindow:
        """
        Get prime productive window for chronotype.

        Args:
            chronotype: User's chronotype

        Returns:
            PrimeWindow: Prime productive time window

        Educational Note:
            Prime windows based on circadian research:
            - EARLY_BIRD: 07:00-11:00 (4h morning peak)
            - INTERMEDIATE: 10:00-16:00 (6h mid-day)
            - NIGHT_OWL: 17:00-22:00 (5h evening peak)
        """
        window = PRIME_WINDOWS.get(chronotype, PRIME_WINDOWS[Chronotype.UNKNOWN])
        logger.debug(
            f"{chronotype.value} → Prime window: "
            f"{window.start.strftime('%H:%M')}-{window.end.strftime('%H:%M')}"
        )
        return window

    def analyze_meq(self, meq_score: Optional[int]) -> tuple[Chronotype, PrimeWindow]:
        """
        Complete analysis: MEQ → Chronotype → Prime Window.

        Args:
            meq_score: MEQ score or None

        Returns:
            tuple[Chronotype, PrimeWindow]: Chronotype and prime window

        Educational Note:
            One-step conversion providing both chronotype
            classification and optimal productive window.
        """
        if meq_score is None:
            chronotype = Chronotype.UNKNOWN
            logger.info("No MEQ score, using UNKNOWN chronotype")
        else:
            chronotype = self.determine_chronotype_from_meq(meq_score)
            logger.info(f"MEQ {meq_score} → {chronotype.value}")

        prime_window = self.get_prime_window(chronotype)
        return chronotype, prime_window


__all__ = [
    "ChronotypeAnalyzer",
    "Chronotype",
    "PrimeWindow",
    "MEQ_RANGES",
    "PRIME_WINDOWS",
]
