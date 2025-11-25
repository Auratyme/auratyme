"""
Energy curve generation from chronotype and sleep patterns.

This module converts chronotype prime windows into realistic 24-hour energy
patterns that the constraint solver uses for optimal task placement.

Educational Note:
    Energy curves represent circadian rhythm patterns. Instead of flat 0.5
    energy across all hours, we model realistic energy fluctuations:
    - Peak energy during prime window (0.9-1.0)
    - Ramp up before prime (gradual increase)
    - Ramp down after prime (gradual decrease)
    - Low energy outside prime (0.3-0.5)
    - Zero energy during sleep (0.0)
    
    This ensures high-focus tasks are scheduled when user has peak cognitive
    performance, respecting their natural circadian rhythm.
"""

import logging
from datetime import time
from typing import Dict, Tuple

from src.core.chronotype.models import Chronotype, PrimeWindow

logger = logging.getLogger(__name__)


def generate_energy_curve_from_chronotype(
    chronotype: Chronotype,
    prime_window: PrimeWindow,
    sleep_bedtime_minutes: int,
    sleep_wake_minutes: int
) -> Dict[int, float]:
    """
    Generates realistic 24-hour energy curve from chronotype and sleep.
    
    Args:
        chronotype: User's chronotype classification
        prime_window: Prime productive window for this chronotype
        sleep_bedtime_minutes: Bedtime in minutes from midnight (e.g., 1245 = 20:45)
        sleep_wake_minutes: Wake time in minutes from midnight (e.g., 360 = 06:00)
    
    Returns:
        Dict mapping hour (0-23) to energy level (0.0-1.0)
    
    Educational Note:
        This function creates a realistic energy curve that:
        1. Respects sleep schedule (0.0 during sleep)
        2. Models circadian rhythm (peak during prime window)
        3. Includes smooth transitions (ramp up/down)
        4. Differentiates chronotypes (early vs night owls)
    """
    prime_start_hour = prime_window.start.hour
    prime_end_hour = prime_window.end.hour
    sleep_bedtime_hour = sleep_bedtime_minutes // 60
    sleep_wake_hour = sleep_wake_minutes // 60
    
    energy_curve = {}
    
    for hour in range(24):
        energy_curve[hour] = _calculate_energy_for_hour(
            hour=hour,
            prime_start=prime_start_hour,
            prime_end=prime_end_hour,
            sleep_bedtime=sleep_bedtime_hour,
            sleep_wake=sleep_wake_hour,
            chronotype=chronotype
        )
    
    _log_energy_curve_summary(energy_curve, chronotype, prime_window)
    
    return energy_curve


def _calculate_energy_for_hour(
    hour: int,
    prime_start: int,
    prime_end: int,
    sleep_bedtime: int,
    sleep_wake: int,
    chronotype: Chronotype
) -> float:
    """
    Calculates energy level for specific hour.
    
    Educational Note:
        Energy calculation follows natural circadian patterns:
        - Sleep hours: 0.0 (no scheduling possible)
        - Prime hours: 0.9-1.0 (peak cognitive performance)
        - Shoulder hours (±1-2h from prime): 0.6-0.8 (good performance)
        - Off-peak hours: 0.3-0.5 (reduced performance)
    """
    if _is_sleep_hour(hour, sleep_bedtime, sleep_wake):
        return 0.0
    
    if _is_prime_hour(hour, prime_start, prime_end):
        return _calculate_prime_energy(hour, prime_start, prime_end)
    
    if _is_shoulder_hour(hour, prime_start, prime_end):
        return _calculate_shoulder_energy(hour, prime_start, prime_end, chronotype)
    
    return _calculate_off_peak_energy(hour, prime_start, chronotype)


def _is_sleep_hour(hour: int, bedtime: int, wake: int) -> bool:
    """
    Checks if hour falls within sleep window.
    
    Educational Note:
        Handles midnight crossing: bedtime 23:00 + wake 07:00 means
        sleep hours are 23, 0, 1, 2, 3, 4, 5, 6 (before 07:00).
    """
    if bedtime > wake:
        return hour >= bedtime or hour < wake
    else:
        return bedtime <= hour < wake


def _is_prime_hour(hour: int, prime_start: int, prime_end: int) -> bool:
    """
    Checks if hour is within prime productive window.
    """
    return prime_start <= hour < prime_end


def _is_shoulder_hour(hour: int, prime_start: int, prime_end: int) -> bool:
    """
    Checks if hour is adjacent to prime window (±2 hours).
    
    Educational Note:
        Shoulder hours represent transition zones where energy
        is ramping up toward prime or winding down after prime.
    """
    return (prime_start - 2 <= hour < prime_start) or (prime_end <= hour < prime_end + 2)


def _calculate_prime_energy(hour: int, prime_start: int, prime_end: int) -> float:
    """
    Calculates energy during prime window (0.9-1.0).
    
    Educational Note:
        Peak energy in middle of prime window, slightly lower
        at edges for smooth transitions.
    """
    prime_middle = (prime_start + prime_end) / 2
    distance_from_middle = abs(hour - prime_middle)
    max_distance = (prime_end - prime_start) / 2
    
    if max_distance > 0:
        energy = 1.0 - (distance_from_middle / max_distance) * 0.1
    else:
        energy = 1.0
    
    return max(0.9, energy)


def _calculate_shoulder_energy(
    hour: int,
    prime_start: int,
    prime_end: int,
    chronotype: Chronotype
) -> float:
    """
    Calculates energy in shoulder hours (0.6-0.8).
    
    Educational Note:
        Energy ramps up smoothly before prime window and
        ramps down after. Chronotype affects ramp steepness:
        - Early birds: steep morning ramp, gradual evening decline
        - Night owls: gradual morning ramp, steep evening energy
    """
    if hour < prime_start:
        distance = prime_start - hour
        if chronotype == Chronotype.EARLY_BIRD:
            return 0.8 - (distance - 1) * 0.15
        elif chronotype == Chronotype.NIGHT_OWL:
            return 0.6 - (distance - 1) * 0.1
        else:
            return 0.7 - (distance - 1) * 0.1
    else:
        distance = hour - prime_end + 1
        if chronotype == Chronotype.EARLY_BIRD:
            return 0.8 - (distance - 1) * 0.1
        elif chronotype == Chronotype.NIGHT_OWL:
            return 0.8 - (distance - 1) * 0.15
        else:
            return 0.7 - (distance - 1) * 0.1


def _calculate_off_peak_energy(hour: int, prime_start: int, chronotype: Chronotype) -> float:
    """
    Calculates energy outside prime and shoulder hours (0.3-0.5).
    
    Educational Note:
        Off-peak energy varies by chronotype:
        - Early birds: low energy in late evening (0.3)
        - Night owls: low energy in early morning (0.3)
        - Intermediate: moderate throughout (0.4-0.5)
    """
    if chronotype == Chronotype.EARLY_BIRD:
        if hour >= 20:
            return 0.3
        elif hour <= 6:
            return 0.4
        else:
            return 0.5
    
    elif chronotype == Chronotype.NIGHT_OWL:
        if hour <= 9:
            return 0.3
        elif hour >= 22:
            return 0.5
        else:
            return 0.4
    
    else:
        return 0.4


def _log_energy_curve_summary(
    energy_curve: Dict[int, float],
    chronotype: Chronotype,
    prime_window: PrimeWindow
) -> None:
    """
    Logs energy curve summary for debugging.
    
    Educational Note:
        Comprehensive logging helps validate energy curves are
        realistic and match expected circadian patterns.
    """
    logger.info("")
    logger.info("⚡ ENERGY CURVE GENERATION:")
    logger.info(f"   Chronotype: {chronotype.value}")
    logger.info(f"   Prime Window: {prime_window.start.strftime('%H:%M')}-{prime_window.end.strftime('%H:%M')}")
    
    peak_hours = [h for h, e in energy_curve.items() if e >= 0.9]
    good_hours = [h for h, e in energy_curve.items() if 0.7 <= e < 0.9]
    moderate_hours = [h for h, e in energy_curve.items() if 0.4 <= e < 0.7]
    low_hours = [h for h, e in energy_curve.items() if 0.0 < e < 0.4]
    sleep_hours = [h for h, e in energy_curve.items() if e == 0.0]
    
    logger.info(f"   Peak energy hours (≥0.9): {len(peak_hours)} hours")
    logger.info(f"   Good energy hours (0.7-0.9): {len(good_hours)} hours")
    logger.info(f"   Moderate energy hours (0.4-0.7): {len(moderate_hours)} hours")
    logger.info(f"   Low energy hours (<0.4): {len(low_hours)} hours")
    logger.info(f"   Sleep hours (0.0): {len(sleep_hours)} hours")
    logger.info("")
