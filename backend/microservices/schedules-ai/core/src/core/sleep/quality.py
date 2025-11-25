"""
Sleep quality analysis orchestration.

This module provides the main quality analysis function that combines
duration, timing, and physiological scoring into an overall quality score.

Educational Note:
    Quality analysis is separated from scoring functions to maintain
    clear separation of concerns: this module handles validation and
    orchestration, while scoring modules implement specific algorithms.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from src.core.sleep.models import SleepMetrics
from src.core.sleep.scoring import (
    calculate_duration_score,
    calculate_physiological_score,
    calculate_timing_score,
)

logger = logging.getLogger(__name__)


def _validate_sleep_analysis_inputs(
    recommended: SleepMetrics,
    sleep_start: datetime,
    sleep_end: datetime
) -> None:
    """
    Validate inputs for sleep quality analysis.

    Args:
        recommended: Recommended sleep metrics
        sleep_start: Actual sleep start time
        sleep_end: Actual sleep end time

    Raises:
        ValueError: If any input is invalid

    Educational Note:
        Early validation prevents cryptic errors later in the
        analysis pipeline and provides clear feedback to users.
    """
    if not isinstance(recommended, SleepMetrics):
        raise ValueError("Recommended must be SleepMetrics object")
    
    if not isinstance(sleep_start, datetime):
        raise ValueError("sleep_start must be datetime")
    
    if not isinstance(sleep_end, datetime):
        raise ValueError("sleep_end must be datetime")
    
    if sleep_end <= sleep_start:
        raise ValueError("sleep_end must be after sleep_start")
    
    if sleep_start.tzinfo is None or sleep_end.tzinfo is None:
        logger.warning(
            "Analyzing sleep with naive datetimes; "
            "results may be inaccurate if timezone differs"
        )


def _extract_actual_sleep_times(
    sleep_start: datetime,
    sleep_end: datetime
) -> tuple:
    """
    Extract duration and times from sleep period.

    Args:
        sleep_start: Actual sleep start datetime
        sleep_end: Actual sleep end datetime

    Returns:
        tuple: (duration, bedtime, wake_time)

    Educational Note:
        Converts full datetimes to local time for comparison with
        recommended times, which are typically specified in local time.
    """
    actual_duration = sleep_end - sleep_start
    actual_bedtime = sleep_start.astimezone(None).time()
    actual_wake_time = sleep_end.astimezone(None).time()
    return actual_duration, actual_bedtime, actual_wake_time


def _combine_quality_scores(
    duration_score: float,
    timing_score: float,
    physiological_score: float,
    quality_weights: Dict[str, float]
) -> float:
    """
    Combine component scores using configured weights.

    Args:
        duration_score: Duration component score
        timing_score: Timing component score
        physiological_score: Physiological component score
        quality_weights: Weight distribution across components

    Returns:
        float: Overall quality score 0-100

    Educational Note:
        Weighted combination allows customization of which factors
        matter most for quality assessment, adapting to user priorities.
    """
    total_score = (
        duration_score * quality_weights.get("duration", 0.0) +
        timing_score * quality_weights.get("timing", 0.0) +
        physiological_score * quality_weights.get("physiological", 0.0)
    )
    return max(0.0, min(100.0, total_score))


def analyze_sleep_quality(
    recommended: SleepMetrics,
    sleep_start: datetime,
    sleep_end: datetime,
    heart_rate_data: Optional[List[Tuple[datetime, int]]],
    hrv_data: Optional[List[Tuple[datetime, float]]],
    duration_tolerance_minutes: int,
    duration_penalty_range_minutes: int,
    timing_tolerance_minutes: int,
    timing_penalty_range_minutes: int,
    hr_target_min: int,
    hr_target_max: int,
    hr_penalty_low: int,
    hr_penalty_high: int,
    hrv_target: float,
    hrv_scale: float,
    physio_weights: Dict[str, float],
    quality_weights: Dict[str, float]
) -> SleepMetrics:
    """
    Analyze sleep quality against recommendations.

    Args:
        recommended: Recommended sleep metrics
        sleep_start: Actual sleep start (timezone-aware)
        sleep_end: Actual sleep end (timezone-aware)
        heart_rate_data: List of (datetime, bpm) tuples
        hrv_data: List of (datetime, rmssd_ms) tuples
        duration_tolerance_minutes: Duration tolerance for full score
        duration_penalty_range_minutes: Duration penalty range
        timing_tolerance_minutes: Timing tolerance for full score
        timing_penalty_range_minutes: Timing penalty range
        hr_target_min: Minimum target HR
        hr_target_max: Maximum target HR
        hr_penalty_low: HR penalty range below target
        hr_penalty_high: HR penalty range above target
        hrv_target: Target average RMSSD
        hrv_scale: HRV scoring scale factor
        physio_weights: Weights for HR vs HRV
        quality_weights: Weights for duration/timing/physiological

    Returns:
        SleepMetrics: Updated metrics with actual values and quality score

    Raises:
        ValueError: If inputs are invalid

    Educational Note:
        This function orchestrates the complete quality analysis workflow,
        delegating specific calculations to focused scoring functions while
        maintaining clean separation of concerns.
    """
    _validate_sleep_analysis_inputs(recommended, sleep_start, sleep_end)

    logger.info(
        f"Analyzing sleep quality. Recommended: "
        f"{recommended.ideal_bedtime.strftime('%H:%M')}-"
        f"{recommended.ideal_wake_time.strftime('%H:%M')}"
    )
    logger.info(f"Actual: {sleep_start} to {sleep_end}")

    actual_duration, actual_bedtime, actual_wake_time = (
        _extract_actual_sleep_times(sleep_start, sleep_end)
    )

    duration_score = calculate_duration_score(
        actual_duration,
        recommended.ideal_duration,
        duration_tolerance_minutes,
        duration_penalty_range_minutes
    )

    timing_score = calculate_timing_score(
        actual_bedtime,
        actual_wake_time,
        recommended.ideal_bedtime,
        recommended.ideal_wake_time,
        timing_tolerance_minutes,
        timing_penalty_range_minutes
    )

    physiological_score = calculate_physiological_score(
        heart_rate_data,
        hrv_data,
        hr_target_min,
        hr_target_max,
        hr_penalty_low,
        hr_penalty_high,
        hrv_target,
        hrv_scale,
        physio_weights
    )

    sleep_quality_score = _combine_quality_scores(
        duration_score,
        timing_score,
        physiological_score,
        quality_weights
    )

    logger.info(f"Sleep quality analysis complete: {sleep_quality_score:.1f}/100")

    return SleepMetrics(
        ideal_duration=recommended.ideal_duration,
        ideal_bedtime=recommended.ideal_bedtime,
        ideal_wake_time=recommended.ideal_wake_time,
        actual_duration=actual_duration,
        actual_bedtime=actual_bedtime,
        actual_wake_time=actual_wake_time,
        sleep_quality_score=sleep_quality_score,
    )
