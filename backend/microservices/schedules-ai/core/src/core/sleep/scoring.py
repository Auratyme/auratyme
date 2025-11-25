"""
Sleep quality scoring functions.

This module provides granular scoring functions for different aspects of
sleep quality: duration, timing, and physiological metrics.

Educational Note:
    Breaking scoring into separate functions enables independent testing
    and adjustment of scoring criteria without affecting other components.
"""

import logging
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def _time_to_minutes(t: time) -> int:
    """
    Convert time to minutes since midnight.

    Args:
        t: Time to convert

    Returns:
        int: Minutes since midnight

    Educational Note:
        Simplifies time arithmetic by working in a linear minute space
        rather than hour:minute pairs.
    """
    return t.hour * 60 + t.minute


def _calculate_duration_penalty(
    diff_minutes: float,
    tolerance_minutes: int,
    penalty_range_minutes: int
) -> float:
    """
    Calculate penalty for duration deviation.

    Args:
        diff_minutes: Absolute difference from ideal
        tolerance_minutes: No penalty within this range
        penalty_range_minutes: Full penalty at this deviation

    Returns:
        float: Penalty points (0 to 100)

    Educational Note:
        Linear penalty function allows configurable tolerance and
        penalty slope for different sleep quality standards.
    """
    if diff_minutes <= tolerance_minutes:
        return 0.0
    
    excess_minutes = diff_minutes - tolerance_minutes
    penalty = excess_minutes * (100.0 / max(1, penalty_range_minutes))
    return min(100.0, penalty)


def calculate_duration_score(
    actual: timedelta,
    ideal: timedelta,
    tolerance_minutes: int,
    penalty_range_minutes: int
) -> float:
    """
    Calculate duration component of sleep quality score.

    Args:
        actual: Actual sleep duration
        ideal: Ideal sleep duration
        tolerance_minutes: No penalty within this range
        penalty_range_minutes: Full penalty at this deviation

    Returns:
        float: Score 0-100

    Educational Note:
        Penalizes both too little and too much sleep, as both
        can indicate poor sleep quality or scheduling issues.
    """
    diff_minutes = abs(actual.total_seconds() - ideal.total_seconds()) / 60.0
    penalty = _calculate_duration_penalty(
        diff_minutes,
        tolerance_minutes,
        penalty_range_minutes
    )
    score = max(0.0, 100.0 - penalty)
    logger.debug(f"Duration score: {score:.1f} (diff: {diff_minutes:.0f}m)")
    return score


def _calculate_time_difference_with_wrap(
    actual_minutes: int,
    ideal_minutes: int
) -> int:
    """
    Calculate minimum time difference handling midnight wrap.

    Args:
        actual_minutes: Actual time in minutes since midnight
        ideal_minutes: Ideal time in minutes since midnight

    Returns:
        int: Minimum difference in minutes

    Educational Note:
        Midnight wrap-around requires special handling: 23:30 to 00:30
        is 60 minutes, not 1410 minutes (going backward through the day).
    """
    direct_diff = abs(actual_minutes - ideal_minutes)
    wrapped_diff = 1440 - direct_diff
    return min(direct_diff, wrapped_diff)


def _calculate_timing_component_score(
    actual_minutes: int,
    ideal_minutes: int,
    tolerance_minutes: int,
    penalty_range_minutes: int,
    max_component_score: float
) -> float:
    """
    Calculate score for one timing component (bedtime or wake time).

    Args:
        actual_minutes: Actual time in minutes
        ideal_minutes: Ideal time in minutes
        tolerance_minutes: No penalty within this range
        penalty_range_minutes: Full penalty at this deviation
        max_component_score: Maximum score for this component

    Returns:
        float: Component score

    Educational Note:
        Each timing component (bedtime and wake time) is scored
        independently, then combined for overall timing score.
    """
    diff_minutes = _calculate_time_difference_with_wrap(
        actual_minutes,
        ideal_minutes
    )
    
    if diff_minutes <= tolerance_minutes:
        return max_component_score
    
    excess_minutes = diff_minutes - tolerance_minutes
    penalty = excess_minutes * (max_component_score / max(1, penalty_range_minutes))
    return max(0.0, max_component_score - penalty)


def calculate_timing_score(
    actual_bed: time,
    actual_wake: time,
    ideal_bed: time,
    ideal_wake: time,
    tolerance_minutes: int,
    penalty_range_minutes: int
) -> float:
    """
    Calculate timing component of sleep quality score.

    Args:
        actual_bed: Actual bedtime
        actual_wake: Actual wake time
        ideal_bed: Ideal bedtime
        ideal_wake: Ideal wake time
        tolerance_minutes: No penalty within this range
        penalty_range_minutes: Full penalty at this deviation

    Returns:
        float: Score 0-100

    Educational Note:
        Splits timing into bedtime and wake time scores to identify
        whether sleep timing issues occur at sleep onset or wake time.
    """
    actual_bed_m = _time_to_minutes(actual_bed)
    ideal_bed_m = _time_to_minutes(ideal_bed)
    actual_wake_m = _time_to_minutes(actual_wake)
    ideal_wake_m = _time_to_minutes(ideal_wake)

    bed_score = _calculate_timing_component_score(
        actual_bed_m,
        ideal_bed_m,
        tolerance_minutes,
        penalty_range_minutes,
        50.0
    )

    wake_score = _calculate_timing_component_score(
        actual_wake_m,
        ideal_wake_m,
        tolerance_minutes,
        penalty_range_minutes,
        50.0
    )

    total_score = bed_score + wake_score
    bed_diff = _calculate_time_difference_with_wrap(actual_bed_m, ideal_bed_m)
    wake_diff = _calculate_time_difference_with_wrap(actual_wake_m, ideal_wake_m)
    
    logger.debug(
        f"Timing score: {total_score:.1f} "
        f"(bed diff: {bed_diff}m, wake diff: {wake_diff}m)"
    )
    return total_score


def _extract_valid_heart_rates(
    heart_rate_data: List[Tuple[datetime, int]]
) -> List[int]:
    """
    Extract valid heart rate values.

    Args:
        heart_rate_data: List of (datetime, bpm) tuples

    Returns:
        List[int]: Valid heart rate values

    Educational Note:
        Filters out zero or invalid readings that could skew
        physiological quality assessment.
    """
    return [hr for _, hr in heart_rate_data if hr > 0]


def _calculate_hr_score(
    valid_hrs: List[int],
    hr_target_min: int,
    hr_target_max: int,
    hr_penalty_low: int,
    hr_penalty_high: int,
    max_score: float
) -> float:
    """
    Calculate heart rate component score.

    Args:
        valid_hrs: List of valid heart rate readings
        hr_target_min: Minimum target HR (bpm)
        hr_target_max: Maximum target HR (bpm)
        hr_penalty_low: Penalty range below target
        hr_penalty_high: Penalty range above target
        max_score: Maximum score for this component

    Returns:
        float: HR component score

    Educational Note:
        Lower resting heart rate during sleep generally indicates
        better cardiovascular recovery and sleep quality.
    """
    if not valid_hrs:
        logger.warning("No valid HR values")
        return 0.0
    
    min_hr = min(valid_hrs)
    
    if hr_target_min <= min_hr <= hr_target_max:
        score = max_score
    elif min_hr < hr_target_min:
        below_target = hr_target_min - min_hr
        penalty = below_target * (max_score / max(1, hr_penalty_low))
        score = max(0.0, max_score - penalty)
    else:
        above_target = min_hr - hr_target_max
        penalty = above_target * (max_score / max(1, hr_penalty_high))
        score = max(0.0, max_score - penalty)
    
    logger.debug(f"HR score: {score:.1f} (min HR: {min_hr})")
    return score


def _calculate_hrv_score(
    valid_hrvs: List[float],
    hrv_target: float,
    hrv_scale: float,
    max_score: float
) -> float:
    """
    Calculate HRV component score.

    Args:
        valid_hrvs: List of valid HRV readings (RMSSD in ms)
        hrv_target: Target average RMSSD
        hrv_scale: Scaling factor for score calculation
        max_score: Maximum score for this component

    Returns:
        float: HRV component score

    Educational Note:
        Higher HRV typically indicates better autonomic nervous system
        recovery and lower stress during sleep.
    """
    if not valid_hrvs:
        logger.warning("No valid HRV values")
        return 0.0
    
    avg_hrv = sum(valid_hrvs) / len(valid_hrvs)
    ratio = avg_hrv / max(1, hrv_target)
    score = min(max_score, max_score * ratio * hrv_scale)
    score = max(0.0, score)
    
    logger.debug(f"HRV score: {score:.1f} (avg RMSSD: {avg_hrv:.1f}ms)")
    return score


def calculate_physiological_score(
    heart_rate_data: Optional[List[Tuple[datetime, int]]],
    hrv_data: Optional[List[Tuple[datetime, float]]],
    hr_target_min: int,
    hr_target_max: int,
    hr_penalty_low: int,
    hr_penalty_high: int,
    hrv_target: float,
    hrv_scale: float,
    physio_weights: Dict[str, float]
) -> float:
    """
    Calculate physiological component of sleep quality score.

    Args:
        heart_rate_data: List of (datetime, bpm) tuples
        hrv_data: List of (datetime, rmssd_ms) tuples
        hr_target_min: Minimum target HR
        hr_target_max: Maximum target HR
        hr_penalty_low: Penalty range below target
        hr_penalty_high: Penalty range above target
        hrv_target: Target average RMSSD
        hrv_scale: HRV scoring scale factor
        physio_weights: Weight distribution between HR and HRV

    Returns:
        float: Score 0-100

    Educational Note:
        Adapts scoring weights based on available data (HR only,
        HRV only, or both) to provide meaningful scores regardless
        of which sensors user has available.
    """
    hr_score = 0.0
    hrv_score = 0.0
    hr_weight = physio_weights.get("hr", 0.5)
    hrv_weight = physio_weights.get("hrv", 0.5)

    has_hr = bool(heart_rate_data)
    has_hrv = bool(hrv_data)

    if not has_hr and not has_hrv:
        logger.debug("No physiological data available")
        return 0.0
    elif has_hr and not has_hrv:
        hr_weight = 1.0
        hrv_weight = 0.0
    elif not has_hr and has_hrv:
        hr_weight = 0.0
        hrv_weight = 1.0

    if has_hr:
        try:
            valid_hrs = _extract_valid_heart_rates(heart_rate_data)  # type: ignore
            hr_score = _calculate_hr_score(
                valid_hrs,
                hr_target_min,
                hr_target_max,
                hr_penalty_low,
                hr_penalty_high,
                100.0 * hr_weight
            )
        except Exception as e:
            logger.error(f"HR score error: {e}")

    if has_hrv:
        try:
            valid_hrvs = [hrv for _, hrv in hrv_data if hrv > 0]  # type: ignore
            hrv_score = _calculate_hrv_score(
                valid_hrvs,
                hrv_target,
                hrv_scale,
                100.0 * hrv_weight
            )
        except Exception as e:
            logger.error(f"HRV score error: {e}")

    total_score = hr_score + hrv_score
    logger.debug(f"Physiological score: {total_score:.1f}")
    return total_score
