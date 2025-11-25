"""
Sleep duration guidelines based on age and sleep cycles.

This module calculates sleep duration using:
1. Age - determines cycle length (teens: 50min, adults: 90min)
2. Sleep need - adjusts cycle count (LOW/MEDIUM/HIGH = ±1 cycle)

Educational Note:
    Teens (<18): 50min cycles, base 11 cycles (9.17h)
    Adults (≥18): 90min cycles, base 5 cycles (7.5h)
    Sleep need adjusts by ±1 cycle from base.
"""

import logging
from datetime import timedelta

from src.core.sleep.models import SleepNeed

logger = logging.getLogger(__name__)


def _is_teen(age: int) -> bool:
    """
    Check if age qualifies as teen for sleep cycle calculation.

    Args:
        age: User's age in years

    Returns:
        bool: True if teen (<18), False otherwise

    Educational Note:
        Teens have different sleep architecture with shorter cycles.
    """
    return age < 18


def _validate_age(age: int) -> None:
    """
    Validate age is within reasonable range.

    Args:
        age: User's age in years

    Raises:
        ValueError: If age is outside valid range (0-120)

    Educational Note:
        Age validation ensures data quality.
    """
    if not (0 <= age <= 120):
        msg = f"Invalid age {age}, must be 0-120"
        logger.error(msg)
        raise ValueError(msg)


def _calculate_cycle_duration(
    age: int,
    teen_cycle_min: int,
    adult_cycle_min: int
) -> int:
    """
    Get cycle duration based on age.

    Args:
        age: User's age
        teen_cycle_min: Cycle length for teens
        adult_cycle_min: Cycle length for adults

    Returns:
        int: Cycle duration in minutes

    Educational Note:
        Teens (<18) have 50min cycles due to different sleep architecture.
        Adults (≥18) have standard 90min cycles.
    """
    return teen_cycle_min if _is_teen(age) else adult_cycle_min


def _calculate_total_cycles(
    age: int,
    sleep_need: SleepNeed,
    teen_base: int,
    adult_base: int,
    adjustments: dict
) -> int:
    """
    Calculate total sleep cycles from age and need.

    Args:
        age: User's age
        sleep_need: LOW/MEDIUM/HIGH
        teen_base: Base cycles for teens
        adult_base: Base cycles for adults
        adjustments: Sleep need to cycle adjustment

    Returns:
        int: Total number of cycles

    Educational Note:
        Teens: base 11 cycles ± 1
        Adults: base 5 cycles ± 1
    """
    base = teen_base if _is_teen(age) else adult_base
    adj = adjustments.get(sleep_need, 0)
    return base + adj


def get_recommended_sleep_duration(
    age: int,
    sleep_need: SleepNeed,
    teen_cycle_min: int,
    adult_cycle_min: int,
    teen_base_cycles: int,
    adult_base_cycles: int,
    cycle_adjustments: dict
) -> timedelta:
    """
    Calculate sleep duration from age and sleep need using cycles.

    Args:
        age: User's age in years
        sleep_need: LOW/MEDIUM/HIGH cycle adjustment
        teen_cycle_min: Teen cycle duration (50min)
        adult_cycle_min: Adult cycle duration (90min)
        teen_base_cycles: Base cycles for teens (11)
        adult_base_cycles: Base cycles for adults (5)
        cycle_adjustments: Sleep need to cycle count adjustment

    Returns:
        timedelta: Recommended sleep duration

    Raises:
        ValueError: If age is invalid

    Educational Note:
        Teens (<18): 50min cycles, base 11 (LOW=10, MED=11, HIGH=12)
        Adults (≥18): 90min cycles, base 5 (LOW=4, MED=5, HIGH=6)
    """
    _validate_age(age)
    
    cycle_min = _calculate_cycle_duration(age, teen_cycle_min, adult_cycle_min)
    total_cycles = _calculate_total_cycles(
        age, sleep_need, teen_base_cycles, adult_base_cycles, cycle_adjustments
    )
    
    total_minutes = cycle_min * total_cycles
    duration = timedelta(minutes=total_minutes)
    
    hours = total_minutes / 60
    age_type = "teen" if _is_teen(age) else "adult"
    
    logger.debug(
        f"Age {age} ({age_type}): {total_cycles} cycles × {cycle_min}min "
        f"= {hours:.2f}h ({sleep_need.value})"
    )
    
    return duration
