"""
Sleep window calculation and cycle-based wake time suggestions.

This module provides functions to calculate optimal bedtime/wake time windows
and suggest wake times aligned with sleep cycles.

Educational Note:
    Sleep timing recommendations combine chronotype research with sleep
    cycle theory to minimize grogginess by waking between cycles.
"""

import logging
from datetime import date, datetime, time, timedelta
from typing import Dict, List, Optional

from src.core.chronotype.models import Chronotype
from src.core.sleep.models import SleepMetrics

logger = logging.getLogger(__name__)


def _get_age_category_for_timing(age: int) -> str:
    """
    Get age category for chronotype timing adjustments.

    Args:
        age: User's age

    Returns:
        str: Category key

    Educational Note:
        Different ages respond differently to chronotype preferences.
    """
    if age < 18:
        return "teen"
    elif age < 65:
        return "adult"
    else:
        return "senior"


def _apply_chronotype_timing_adjustment(
    age: int,
    chronotype: Chronotype,
    age_chronotype_shifts: Dict[str, Dict[Chronotype, float]]
) -> float:
    """
    Calculate timing shift based on age and chronotype.

    Args:
        age: User's age
        chronotype: User's chronotype
        age_chronotype_shifts: Age category to chronotype shifts

    Returns:
        float: Hours to shift timing (positive=later, negative=earlier)

    Educational Note:
        Age affects chronotype impact:
        - Teens: NIGHT_OWL +1.5h (stronger effect)
        - Adults: NIGHT_OWL +1.0h (moderate)
        - Seniors: EARLY_BIRD -1.5h (stronger morning preference)
    """
    category = _get_age_category_for_timing(age)
    shifts = age_chronotype_shifts.get(category, {})
    shift_hours = shifts.get(chronotype, 0.0)
    
    logger.debug(
        f"Age {age} ({category}) + {chronotype.value} → {shift_hours:+.1f}h shift"
    )
    return shift_hours


def _calculate_adjusted_wake_time(
    target_wake_time: time,
    timing_adjustment_hours: float
) -> time:
    """
    Apply timing adjustment to target wake time.

    Args:
        target_wake_time: Original target wake time
        timing_adjustment_hours: Hours to shift (positive=later)

    Returns:
        time: Adjusted wake time

    Educational Note:
        Handles date arithmetic to correctly shift times across
        midnight boundary when needed.
    """
    reference_date = date.today()
    target_wake_dt = datetime.combine(reference_date, target_wake_time)
    
    if target_wake_time < time(4, 0):
        target_wake_dt += timedelta(days=1)

    adjusted_wake_dt = target_wake_dt + timedelta(hours=timing_adjustment_hours)
    return adjusted_wake_dt.time()


def _calculate_bedtime(wake_datetime: datetime, sleep_duration: timedelta) -> time:
    """
    Calculate bedtime from wake time and duration.

    Args:
        wake_datetime: Full datetime of wake time
        sleep_duration: Total sleep duration

    Returns:
        time: Calculated bedtime

    Educational Note:
        Working backward from wake time ensures the sleep window
        ends at the desired time, which is more intuitive for users.
    """
    bedtime_dt = wake_datetime - sleep_duration
    return bedtime_dt.time()


def calculate_sleep_window(
    age: int,
    chronotype: Chronotype,
    total_time_in_bed: timedelta,
    target_wake_time: Optional[time],
    default_wake_times: Dict[Chronotype, time],
    age_chronotype_shifts: Dict[str, Dict[Chronotype, float]],
    sleep_onset: timedelta
) -> SleepMetrics:
    """
    Calculate sleep window with age-specific chronotype shifts.

    Args:
        age: User's age in years
        chronotype: User's chronotype category (from MEQ score)
        total_time_in_bed: Sleep duration + sleep onset time
        target_wake_time: Optional preferred wake time
        default_wake_times: Chronotype to default wake time mapping
        age_chronotype_shifts: Age-specific chronotype timing shifts
        sleep_onset: Time to fall asleep (typically 15min)

    Returns:
        SleepMetrics: Recommended sleep window

    Raises:
        TypeError: If target_wake_time is not time or None

    Educational Note:
        Chronotype effect varies by age:
        - Teen night owls: +1.5h (stronger delayed phase)
        - Adult night owls: +1.0h (moderate)
        - Senior early birds: -1.5h (stronger advanced phase)
    """
    if target_wake_time is None:
        # Debug: Show what's in the config dict
        logger.info(f"🔍 DEBUG: default_wake_times type: {type(default_wake_times)}")
        logger.info(f"🔍 DEBUG: default_wake_times keys: {list(default_wake_times.keys())}")
        logger.info(f"🔍 DEBUG: chronotype type: {type(chronotype)}, value: {chronotype}, repr: {repr(chronotype)}")
        logger.info(f"🔍 DEBUG: chronotype id: {id(chronotype)}")
        logger.info(f"🔍 DEBUG: Chronotype.EARLY_BIRD id: {id(Chronotype.EARLY_BIRD)}")
        logger.info(f"🔍 DEBUG: chronotype == Chronotype.EARLY_BIRD: {chronotype == Chronotype.EARLY_BIRD}")
        logger.info(f"🔍 DEBUG: chronotype is Chronotype.EARLY_BIRD: {chronotype is Chronotype.EARLY_BIRD}")
        
        # Try direct comparison
        for key in default_wake_times.keys():
            if key == chronotype:
                logger.info(f"🔍 Found matching key: {key}")
                break
        
        target_wake_time = default_wake_times.get(chronotype, time(7, 30))
        logger.info(
            f"📍 Using default wake time {target_wake_time.strftime('%H:%M')} "
            f"for {chronotype.value} (from config: {default_wake_times.get(chronotype, 'NOT FOUND')})"
        )
    else:
        logger.info(
            f"📍 Using user-provided wake time: {target_wake_time.strftime('%H:%M')} "
            f"(overriding default for {chronotype.value})"
        )
    
    if not isinstance(target_wake_time, time):
        raise TypeError("target_wake_time must be datetime.time or None")

    timing_shift_h = _apply_chronotype_timing_adjustment(
        age,
        chronotype,
        age_chronotype_shifts
    )

    reference_date = date.today()
    target_wake_dt = datetime.combine(reference_date, target_wake_time)
    
    if target_wake_time < time(4, 0):
        target_wake_dt += timedelta(days=1)

    adjusted_wake_dt = target_wake_dt + timedelta(hours=timing_shift_h)
    final_wake_time = adjusted_wake_dt.time()

    bedtime_dt = adjusted_wake_dt - total_time_in_bed
    final_bedtime = bedtime_dt.time()
    
    actual_sleep_duration = total_time_in_bed - sleep_onset

    logger.info(
        f"Age {age}, {chronotype.value}: {final_bedtime.strftime('%H:%M')}-"
        f"{final_wake_time.strftime('%H:%M')} "
        f"(shift: {timing_shift_h:+.1f}h, +{int(sleep_onset.total_seconds()/60)}min onset)"
    )
    return SleepMetrics(
        ideal_duration=actual_sleep_duration,
        ideal_bedtime=final_bedtime,
        ideal_wake_time=final_wake_time,
    )


def _calculate_wake_time_for_cycles(
    bedtime: time,
    num_cycles: int,
    sleep_onset_minutes: int,
    cycle_duration_minutes: int
) -> time:
    """
    Calculate wake time for completing N sleep cycles.

    Args:
        bedtime: Time user goes to bed
        num_cycles: Number of complete sleep cycles
        sleep_onset_minutes: Minutes to fall asleep
        cycle_duration_minutes: Duration of one sleep cycle

    Returns:
        time: Suggested wake time

    Educational Note:
        Sleep cycles average 90 minutes. Waking between cycles reduces
        grogginess by avoiding interruption of deep sleep stages.
    """
    reference_date = date.today()
    bedtime_dt = datetime.combine(reference_date, bedtime)
    
    sleep_start_dt = bedtime_dt + timedelta(minutes=sleep_onset_minutes)
    total_duration = timedelta(minutes=num_cycles * cycle_duration_minutes)
    wake_dt = sleep_start_dt + total_duration
    
    logger.debug(
        f"{num_cycles} cycles from {bedtime.strftime('%H:%M')} → "
        f"{wake_dt.strftime('%H:%M')}"
    )
    return wake_dt.time()


def suggest_wake_times_based_on_cycles(
    bedtime: time,
    sleep_onset_minutes: int,
    cycle_duration_minutes: int,
    min_cycles: int = 4,
    max_cycles: int = 6
) -> List[time]:
    """
    Suggest optimal wake times for completing full sleep cycles.

    Args:
        bedtime: Intended bedtime
        sleep_onset_minutes: Minutes to fall asleep
        cycle_duration_minutes: Duration of one sleep cycle
        min_cycles: Minimum cycles to suggest (default: 4)
        max_cycles: Maximum cycles to suggest (default: 6)

    Returns:
        List[time]: Sorted list of suggested wake times

    Educational Note:
        Provides multiple options to accommodate varying sleep needs
        while ensuring each suggestion aligns with sleep cycle boundaries.
    """
    if not isinstance(bedtime, time):
        logger.error(f"Invalid bedtime type: {type(bedtime)}")
        return []
    
    if not (1 <= min_cycles <= max_cycles <= 10):
        logger.error(f"Invalid cycle range: {min_cycles}-{max_cycles}")
        return []

    suggested_times = [
        _calculate_wake_time_for_cycles(
            bedtime,
            num_cycles,
            sleep_onset_minutes,
            cycle_duration_minutes
        )
        for num_cycles in range(min_cycles, max_cycles + 1)
    ]

    return sorted(suggested_times)
