"""
Chronotype classification from MEQ questionnaire.

This module provides MEQ score to chronotype conversion based on
Morningness-Eveningness Questionnaire (Horne & Östberg, 1976).

Educational Note:
    MEQ is a validated 19-item questionnaire scoring 16-86:
    - 16-41: Evening types (Night Owls)
    - 42-58: Intermediate types
    - 59-86: Morning types (Early Birds)
"""

import logging
from typing import Dict, Tuple

from src.core.chronotype.models import Chronotype

logger = logging.getLogger(__name__)


def _validate_meq_score_range(
    meq_score: int,
    meq_ranges: Dict[Tuple[int, int], Chronotype]
) -> None:
    """
    Validate MEQ score is within configured ranges.

    Args:
        meq_score: MEQ questionnaire score
        meq_ranges: Configured score ranges

    Raises:
        ValueError: If ranges are empty or score is out of range

    Educational Note:
        Early validation with clear error messages improves debugging
        and prevents silent failures in classification logic.
    """
    all_scores = [s for r in meq_ranges.keys() for s in r]
    if not all_scores:
        raise ValueError("MEQ ranges configuration is empty")

    valid_range_min = min(all_scores)
    valid_range_max = max(all_scores)

    if not (valid_range_min <= meq_score <= valid_range_max):
        msg = (
            f"Invalid MEQ score: {meq_score}. "
            f"Valid range: {valid_range_min}-{valid_range_max}"
        )
        logger.error(msg)
        raise ValueError(msg)


def determine_chronotype_from_meq(
    meq_score: int,
    meq_ranges: Dict[Tuple[int, int], Chronotype]
) -> Chronotype:
    """
    Determine chronotype from MEQ (Morningness-Eveningness Questionnaire) score.

    Args:
        meq_score: MEQ questionnaire score
        meq_ranges: Score range to chronotype mapping

    Returns:
        Chronotype: Determined chronotype classification

    Raises:
        ValueError: If MEQ score is invalid

    Educational Note:
        MEQ is a validated scientific questionnaire for chronotype
        assessment. This function maps scores to chronotype categories
        using configurable ranges.
    """
    _validate_meq_score_range(meq_score, meq_ranges)

    for score_range, chronotype in meq_ranges.items():
        min_score, max_score = score_range
        if min_score <= meq_score <= max_score:
            logger.debug(
                f"MEQ score {meq_score} → {chronotype.value}"
            )
            return chronotype

    logger.warning(
        f"Could not map MEQ score {meq_score}, "
        f"defaulting to {Chronotype.INTERMEDIATE.value}"
    )
    return Chronotype.INTERMEDIATE



