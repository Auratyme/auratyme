"""
Adaptive sleep window calculation based on fixed events.

This module implements human-like schedule planning by calculating
sleep times FROM fixed events (work, meetings) rather than forcing
fixed events to fit around predetermined sleep times.

Educational Note:
    Real humans plan their day by working backwards from commitments:
    "I have work at 8am → I need to commute 30min → I need morning routine 20min
    → Therefore I must wake at 7:10am"
    
    This is opposite to: "I want to wake at 6am → Now fit work somewhere"
    
    CRITICAL: Sleep onset (15min to fall asleep) is ALWAYS included in bedtime
    calculations to ensure accurate sleep window positioning.
"""

import logging
from datetime import time
from typing import List, Optional, Tuple, TYPE_CHECKING

from src.utils.time_utils import time_to_total_minutes, total_minutes_to_time
from src.core.sleep import SleepMetrics
from src.core.chronotype import Chronotype
from src.core.sleep.config import DEFAULT_WAKE_TIMES, SLEEP_ONSET_MINUTES

if TYPE_CHECKING:
    from src.core.solver import FixedEventInterval

logger = logging.getLogger(__name__)


def calculate_adaptive_sleep_window(
    fixed_events: List["FixedEventInterval"],
    preferences: dict,
    chronotype: Chronotype,
    sleep_need_hours: float,
    user_profile: dict
) -> Tuple[int, int]:
    """
    Calculates optimal wake and bedtime based on fixed events.
    
    ALGORITHM:
    1. Find earliest and latest fixed events
    2. Calculate REQUIRED wake time (working backwards from earliest)
    3. Calculate REQUIRED bedtime (working forwards from latest)
    4. Compare with PREFERRED times from chronotype
    5. Choose optimal times respecting both constraints and preferences
    6. Validate sleep duration meets minimum requirements
    
    Args:
        fixed_events: List of fixed time commitments (work, meetings, etc.)
        preferences: User preferences including routines and work settings
        chronotype: User's chronotype (early_bird, intermediate, night_owl)
        sleep_need_hours: Required sleep duration in hours
        user_profile: User profile data
        
    Returns:
        Tuple of (wake_minutes, bedtime_minutes) from midnight
        
    Educational Note:
        This mirrors human planning: commitments first, sleep adjusted to fit.
        Ensures no conflicts between sleep and mandatory events.
    """
    if not fixed_events:
        return _calculate_from_chronotype_only(chronotype, sleep_need_hours)
    
    earliest_fixed, latest_fixed = _find_fixed_event_boundaries(fixed_events)
    
    required_wake = _calculate_required_wake_time(
        earliest_fixed, preferences
    )
    
    preferred_wake = _get_preferred_wake_from_chronotype(
        chronotype, user_profile
    )
    
    actual_wake = _choose_optimal_wake_time(
        required_wake, preferred_wake, chronotype
    )
    
    actual_bedtime = _calculate_required_bedtime(
        latest_fixed, preferences, actual_wake, sleep_need_hours
    )
    
    actual_bedtime = _adjust_bedtime_for_prime_window(
        actual_bedtime, actual_wake, chronotype, sleep_need_hours
    )
    
    _validate_sleep_duration(
        actual_wake, actual_bedtime, sleep_need_hours
    )
    
    preferred_bedtime = _get_preferred_bedtime_from_chronotype(
        chronotype, user_profile
    )
    
    logger.info(f"📊 ADAPTIVE SLEEP CALCULATION:")
    logger.info(f"   Earliest fixed: {total_minutes_to_time(earliest_fixed).strftime('%H:%M')}")
    logger.info(f"   Latest fixed: {total_minutes_to_time(latest_fixed).strftime('%H:%M')}")
    logger.info(f"   Required wake: {total_minutes_to_time(required_wake).strftime('%H:%M')}")
    logger.info(f"   Preferred wake: {total_minutes_to_time(preferred_wake).strftime('%H:%M')}")
    logger.info(f"   ✅ Actual wake: {total_minutes_to_time(actual_wake).strftime('%H:%M')}")
    logger.info(f"   Preferred bedtime: {total_minutes_to_time(preferred_bedtime).strftime('%H:%M')}")
    logger.info(f"   ✅ Actual bedtime: {total_minutes_to_time(actual_bedtime).strftime('%H:%M')} (adjusted for prime window)")
    
    return actual_wake, actual_bedtime


def _find_fixed_event_boundaries(
    fixed_events: List["FixedEventInterval"]
) -> Tuple[int, int]:
    """
    Finds earliest start and latest end of all fixed events.
    
    Educational Note:
        These boundaries define the "must attend" window where
        user cannot be sleeping or unavailable.
    """
    work_and_meetings = [
        e for e in fixed_events
        if not _is_routine_or_sleep_event(e.id)
    ]
    
    if not work_and_meetings:
        return 480, 960
    
    earliest = min(e.start_minutes for e in work_and_meetings)
    latest = max(e.end_minutes for e in work_and_meetings)
    
    return earliest, latest


def _is_routine_or_sleep_event(event_id: str) -> bool:
    """
    Checks if event is routine or sleep (not a real commitment).
    
    Educational Note:
        We want to find REAL fixed events (work, meetings) to calculate
        wake/bed times, not the routines/sleep we're trying to calculate.
    """
    routine_keywords = ["morning_routine", "evening_routine", "sleep"]
    return any(keyword in event_id.lower() for keyword in routine_keywords)


def _calculate_required_wake_time(
    earliest_fixed_min: int,
    preferences: dict
) -> int:
    """
    Calculates latest possible wake time to make earliest commitment.
    
    Works BACKWARDS from earliest fixed event:
    earliest_fixed ← morning_routine ← WAKE
    
    CRITICAL: earliest_fixed is often already the commute start time
    (e.g., "Commute to Work" at 07:22), so we only subtract morning routine.
    The system already created separate commute fixed events in data_preparation.
    
    Educational Note:
        This is how humans think: "Commute starts at 7:22, need 58min routine
        = I MUST wake by 6:24am at the latest"
        
        We do NOT subtract commute here because earliest_fixed already
        accounts for it (it's the commute start time itself).
    """
    morning_routine_min = _get_morning_routine_duration(preferences)
    
    required_wake = earliest_fixed_min - morning_routine_min
    
    if required_wake < 0:
        required_wake = 0
        logger.warning(f"⚠️ Required wake time before midnight! Setting to 00:00")
    
    return required_wake


def _get_morning_routine_duration(preferences: dict) -> int:
    """
    Extracts morning routine duration from preferences.
    
    Educational Note:
        Default 30min covers: wake up, shower, breakfast, dress.
    """
    routines = preferences.get("routines", {})
    return routines.get("morning_duration_minutes", 30)


def _get_preferred_wake_from_chronotype(
    chronotype: Chronotype,
    user_profile: dict
) -> int:
    """
    Gets user's preferred wake time based on chronotype.
    
    Educational Note:
        Uses centralized DEFAULT_WAKE_TIMES from sleep config to avoid
        duplication. Early birds prefer 06:00, night owls prefer 09:00.
        Commitments can override these preferences when necessary.
    """
    default_wake = DEFAULT_WAKE_TIMES.get(chronotype, time(7, 30))
    return time_to_total_minutes(default_wake)


def _choose_optimal_wake_time(
    required_wake: int,
    preferred_wake: int,
    chronotype: Chronotype
) -> int:
    """
    Chooses optimal wake time balancing requirements and preferences.
    
    LOGIC:
    - required_wake: EARLIEST possible wake time (must wake BY this time for morning routine + earliest fixed event)
    - preferred_wake: Desired wake time based on chronotype
    - If required <= preferred: Use required (MUST wake early for commitments)
    - If required > preferred: Can sleep longer, use preferred
    
    Educational Note:
        Required wake takes PRIORITY - if user has 7am meeting, they MUST wake early enough
        for morning routine, regardless of being night owl. Preferred wake only used when
        there's flexibility (no early commitments).
    """
    if required_wake <= preferred_wake:
        return required_wake
    
    time_difference = required_wake - preferred_wake
    
    if chronotype == Chronotype.EARLY_BIRD and time_difference >= 30:
        logger.info(f"🐦 Early bird can sleep in: {time_difference}min extra sleep available")
        return preferred_wake
    
    if time_difference >= 60:
        logger.info(f"⏰ Can sleep in: {time_difference}min extra sleep available")
        return preferred_wake
    
    return required_wake


def _calculate_required_bedtime(
    latest_fixed_min: int,
    preferences: dict,
    wake_min: int,
    sleep_need_hours: float
) -> int:
    """
    Calculates required bedtime based on sleep needs AND evening routine.
    
    CRITICAL: Bedtime must be AFTER (latest_fixed + evening_routine).
    
    Works in TWO modes:
    1. IDEAL: Backwards from wake: wake - sleep - onset = bedtime
    2. FORCED: If ideal conflicts with commitments: latest_fixed + evening_routine = bedtime
    
    Educational Note:
        User cannot go to bed BEFORE finishing evening routine.
        Evening routine starts AFTER last commitment (work, meeting).
        
        Example with late work:
        - Work ends: 22:00
        - Evening routine: 30min
        - Earliest possible bedtime: 22:30
        - Ideal bedtime (7.5h sleep, 06:00 wake): 22:15
        - CONFLICT! Must use 22:30 (forced mode)
    """
    sleep_need_min = int(sleep_need_hours * 60)
    sleep_onset_min = SLEEP_ONSET_MINUTES
    total_time_needed = sleep_need_min + sleep_onset_min
    
    ideal_bedtime = wake_min - total_time_needed
    if ideal_bedtime < 0:
        ideal_bedtime += 1440
    
    evening_routine_min = _get_evening_routine_duration(preferences)
    earliest_possible_bedtime = latest_fixed_min + evening_routine_min
    
    if earliest_possible_bedtime >= 1440:
        earliest_possible_bedtime -= 1440
    
    if ideal_bedtime < earliest_possible_bedtime:
        if earliest_possible_bedtime - ideal_bedtime > 720:
            logger.info(f"✅ Ideal bedtime {ideal_bedtime}min (after midnight) is AFTER evening routine {earliest_possible_bedtime}min")
            required_bedtime = ideal_bedtime
        else:
            logger.warning(f"⚠️ Bedtime conflict: ideal={ideal_bedtime}min, but must wait until {earliest_possible_bedtime}min (work + evening routine)")
            required_bedtime = earliest_possible_bedtime
    else:
        required_bedtime = ideal_bedtime
    
    logger.info(f"✅ Sleep duration: {sleep_need_hours:.1f}h actual sleep (need: {sleep_need_hours:.1f}h) + {sleep_onset_min}min onset")
    
    return required_bedtime


def _adjust_bedtime_for_prime_window(
    bedtime_min: int,
    wake_min: int,
    chronotype: Chronotype,
    sleep_need_hours: float
) -> int:
    """
    Adjusts bedtime to avoid blocking prime energy window for night owls.
    
    CRITICAL FOR NIGHT OWL SCHEDULES:
        Prime window 17:00-22:00 (5 hours) must remain FREE for high-priority tasks.
        If calculated bedtime falls WITHIN prime window, push it to AFTER 22:00.
    
    Logic:
        1. If NOT night_owl → return bedtime unchanged
        2. If bedtime < 22:00 (1320min) → push to 22:15 (allows some evening flex)
        3. Validate: New bedtime provides required sleep (within 30min tolerance)
        4. If sleep deficit > 30min → revert to original bedtime (sleep priority!)
    
    Educational Note:
        This balances prime window optimization with sleep need.
        For HIGH sleep need (9h), we may need to start earlier (e.g., 21:00)
        to avoid excessive deficit. For LOW sleep need (6h), we can safely
        push to 22:15 and still get enough sleep.
        
        Example:
        - LOW sleep (6h): 22:15→07:00 = 8.75h OK (2.75h buffer)
        - MEDIUM sleep (7.5h): 22:15→07:00 = 8.75h OK (1.25h buffer)
        - HIGH sleep (9h): 22:15→07:00 = 8.75h DEFICIT (0.25h short) - REJECT
    """
    if chronotype != Chronotype.NIGHT_OWL:
        return bedtime_min
    
    prime_window_end = 22 * 60
    
    if bedtime_min >= prime_window_end:
        logger.info(f"✅ Bedtime {total_minutes_to_time(bedtime_min).strftime('%H:%M')} already after prime window (22:00)")
        return bedtime_min
    
    if bedtime_min < 300:
        logger.info(f"✅ Bedtime {total_minutes_to_time(bedtime_min).strftime('%H:%M')} is after midnight (late night sleep), keeping original bedtime")
        return bedtime_min
    
    adjusted_bedtime = prime_window_end + 15
    
    sleep_need_min = int(sleep_need_hours * 60)
    sleep_onset_min = SLEEP_ONSET_MINUTES
    
    if adjusted_bedtime > wake_min:
        actual_sleep_duration = (wake_min + 1440) - adjusted_bedtime - sleep_onset_min
    else:
        actual_sleep_duration = wake_min - adjusted_bedtime - sleep_onset_min
    
    sleep_deficit = sleep_need_min - actual_sleep_duration
    
    if sleep_need_hours >= 8.5:
        max_tolerable_deficit = 0
    elif sleep_need_hours >= 7.0:
        max_tolerable_deficit = 15
    else:
        max_tolerable_deficit = 30
    
    if sleep_deficit <= max_tolerable_deficit:
        if sleep_deficit < 0:
            logger.info(f"🌙 NIGHT OWL: Adjusted bedtime {total_minutes_to_time(bedtime_min).strftime('%H:%M')} → {total_minutes_to_time(adjusted_bedtime).strftime('%H:%M')} (frees prime window 17:00-22:00, surplus: {-sleep_deficit}min)")
        else:
            logger.info(f"🌙 NIGHT OWL: Adjusted bedtime {total_minutes_to_time(bedtime_min).strftime('%H:%M')} → {total_minutes_to_time(adjusted_bedtime).strftime('%H:%M')} (frees prime window 17:00-22:00, deficit: {sleep_deficit}min)")
        return adjusted_bedtime
    else:
        logger.warning(f"⚠️ Cannot adjust bedtime to {total_minutes_to_time(adjusted_bedtime).strftime('%H:%M')} - would cause {sleep_deficit}min sleep deficit (need {sleep_need_hours:.1f}h, get {actual_sleep_duration/60:.1f}h). Keeping original bedtime to prioritize sleep.")
        return bedtime_min


def _get_evening_routine_duration(preferences: dict) -> int:
    """
    Extracts evening routine duration from preferences.
    
    Educational Note:
        Default 45min covers: dinner, wind down, prep for bed.
    """
    routines = preferences.get("routines", {})
    return routines.get("evening_duration_minutes", 45)


def _get_preferred_bedtime_from_chronotype(
    chronotype: Chronotype,
    user_profile: dict
) -> int:
    """
    Gets user's preferred bedtime based on chronotype.
    
    Educational Note:
        Calculates preferred bedtime by working backwards from preferred
        wake time. Uses DEFAULT_WAKE_TIMES and typical sleep duration
        to determine natural bedtime preference.
        
        Early birds: wake 06:00 - 9h = bedtime 21:00
        Night owls: wake 09:00 - 9h = bedtime 00:00 (midnight)
    """
    preferred_wake = DEFAULT_WAKE_TIMES.get(chronotype, time(7, 30))
    wake_min = time_to_total_minutes(preferred_wake)
    
    typical_sleep_hours = 9
    sleep_need_min = typical_sleep_hours * 60
    sleep_onset_min = SLEEP_ONSET_MINUTES
    
    bed_min = wake_min - sleep_need_min - sleep_onset_min
    
    if bed_min < 0:
        bed_min += 1440
    
    if bed_min == 0:
        bed_min = 1439
    
    return bed_min


def _choose_optimal_bedtime(
    required_bedtime: int,
    preferred_bedtime: int,
    wake_min: int,
    sleep_need_hours: float
) -> int:
    """
    Chooses optimal bedtime balancing requirements and preferences.
    
    PRIORITY: Must get enough sleep!
    
    Educational Note:
        Unlike wake time, bedtime is more flexible - people can stay up
        later if they want, but they MUST get minimum sleep including
        the 15min sleep onset buffer.
        
        Handles midnight crossing: bedtime after midnight (e.g., 01:00)
        is represented as minutes within 0-1439 range for current day.
    """
    sleep_need_min = int(sleep_need_hours * 60)
    sleep_onset_min = SLEEP_ONSET_MINUTES
    total_time_needed = sleep_need_min + sleep_onset_min
    
    latest_bedtime_for_sleep = wake_min - total_time_needed
    if latest_bedtime_for_sleep < 0:
        latest_bedtime_for_sleep += 1440
    
    if required_bedtime > 1440:
        required_bedtime -= 1440
    
    if preferred_bedtime > 1440:
        preferred_bedtime -= 1440
    
    candidate_bedtime = max(required_bedtime, preferred_bedtime)
    
    if candidate_bedtime <= latest_bedtime_for_sleep:
        final_bedtime = candidate_bedtime
    elif latest_bedtime_for_sleep >= required_bedtime:
        final_bedtime = latest_bedtime_for_sleep
    else:
        logger.warning(
            f"⚠️ Sleep conflict! Required bedtime {total_minutes_to_time(required_bedtime).strftime('%H:%M')} "
            f"too late for {sleep_need_hours}h sleep (+ {sleep_onset_min}min onset) before wake {total_minutes_to_time(wake_min).strftime('%H:%M')}. "
            f"Adjusting bedtime to {total_minutes_to_time(latest_bedtime_for_sleep).strftime('%H:%M')}"
        )
        final_bedtime = max(required_bedtime, latest_bedtime_for_sleep - 60)
    
    if final_bedtime < 0:
        final_bedtime += 1440
    
    if final_bedtime == 0:
        final_bedtime = 1439
    
    return final_bedtime


def _validate_sleep_duration(
    wake_min: int,
    bed_min: int,
    sleep_need_hours: float
) -> None:
    """
    Validates that calculated sleep window provides sufficient rest.
    
    Educational Note:
        Final safety check considering sleep_onset. Warns if user won't
        get enough ACTUAL SLEEP (excluding 15min to fall asleep) due to
        conflicting commitments. Minimum acceptable: 5 hours actual sleep.
    """
    if bed_min > wake_min:
        sleep_duration_min = (wake_min + 1440) - bed_min
    else:
        sleep_duration_min = wake_min - bed_min
    
    sleep_onset_min = SLEEP_ONSET_MINUTES
    actual_sleep_min = sleep_duration_min - sleep_onset_min
    sleep_need_min = int(sleep_need_hours * 60)
    
    actual_sleep_hours = actual_sleep_min / 60
    
    if actual_sleep_min < sleep_need_min:
        deficit_min = sleep_need_min - actual_sleep_min
        logger.error(
            f"❌ SLEEP DEFICIT: {actual_sleep_hours:.1f}h actual sleep vs {sleep_need_hours:.1f}h needed. "
            f"Deficit: {deficit_min}min ({deficit_min/60:.1f}h) - excluding {sleep_onset_min}min sleep onset"
        )
    else:
        logger.info(
            f"✅ Sleep duration: {actual_sleep_hours:.1f}h actual sleep "
            f"(need: {sleep_need_hours:.1f}h) + {sleep_onset_min}min onset"
        )


def _calculate_from_chronotype_only(
    chronotype: Chronotype,
    sleep_need_hours: float
) -> Tuple[int, int]:
    """
    Calculates sleep window purely from chronotype when no fixed events.
    
    Educational Note:
        Used for free days/weekends where user has no commitments.
        Pure preference-based scheduling including sleep_onset buffer.
        
        Example: Night owl, 9h sleep need
        - Preferred wake: 09:00 (540min)
        - Sleep needed: 9h (540min) + 15min onset = 555min
        - Bedtime: 540 - 555 = -15 → +1440 = 1425min → 23:45
    """
    wake_time = DEFAULT_WAKE_TIMES.get(chronotype, time(7, 30))
    wake_min = time_to_total_minutes(wake_time)
    
    sleep_need_min = int(sleep_need_hours * 60)
    sleep_onset_min = SLEEP_ONSET_MINUTES
    total_time_needed = sleep_need_min + sleep_onset_min
    
    bed_min = wake_min - total_time_needed
    
    if bed_min < 0:
        bed_min += 1440
    
    logger.info(f"📅 Free day schedule (no fixed events)")
    logger.info(f"   Wake: {wake_time.strftime('%H:%M')}")
    logger.info(f"   Bedtime: {total_minutes_to_time(bed_min).strftime('%H:%M')} (includes {sleep_onset_min}min onset)")
    
    return wake_min, bed_min
