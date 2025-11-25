"""
Sleep window calculation for schedule generation.

This module handles sleep recommendations based on user profiles and preferences.
"""

import logging
from datetime import time, timedelta, datetime
from typing import TYPE_CHECKING, Optional

from src.core.sleep import SleepMetrics
from src.core.sleep.models import SleepNeed

if TYPE_CHECKING:
    from src.core.sleep import SleepCalculator
    from src.core.scheduler.models import ScheduleInputData, ScheduleChronotypeContext

logger = logging.getLogger(__name__)


def _convert_scale_to_sleep_need(sleep_need_scale: Optional[float]) -> SleepNeed:
    """
    Convert sleep need scale (0-100) to SleepNeed enum.
    
    Args:
        sleep_need_scale: User preference scale 0-100
        
    Returns:
        SleepNeed: LOW (<40), MEDIUM (40-60), HIGH (>60)
        
    Educational Note:
        Maps continuous preference scale to discrete sleep need categories,
        allowing flexible user input while maintaining simple sleep calculation.
    """
    if sleep_need_scale is None:
        return SleepNeed.MEDIUM
    
    if sleep_need_scale < 40:
        return SleepNeed.LOW
    elif sleep_need_scale <= 60:
        return SleepNeed.MEDIUM
    else:
        return SleepNeed.HIGH


def _convert_string_to_sleep_need(sleep_need_str: Optional[str]) -> SleepNeed:
    """
    Convert sleep need string to SleepNeed enum.
    
    Args:
        sleep_need_str: "low", "medium", or "high"
        
    Returns:
        SleepNeed: Corresponding enum value
        
    Educational Note:
        Provides direct string-to-enum conversion for user profile data
        that explicitly specifies sleep need category.
    """
    if not sleep_need_str:
        return SleepNeed.MEDIUM
    
    sleep_need_lower = sleep_need_str.lower()
    
    if sleep_need_lower == "low":
        return SleepNeed.LOW
    elif sleep_need_lower == "high":
        return SleepNeed.HIGH
    else:
        return SleepNeed.MEDIUM


def calculate_sleep_window(
    sleep_calculator: "SleepCalculator",
    chronotype_context: "ScheduleChronotypeContext",
    input_data: "ScheduleInputData"
) -> SleepMetrics:
    """
    Calculates the recommended sleep window.
    
    Educational Note:
        Sleep calculation considers multiple factors: age-based needs,
        chronotype-specific timing, and user preferences. Fallback ensures
        schedule generation continues even when calculation fails.
    """
    prefs = input_data.preferences
    target_wake = _parse_preferred_wake_time(prefs)
    
    try:
        sleep_metrics = _calculate_with_preferences(
            sleep_calculator, chronotype_context, input_data, prefs, target_wake
        )
        _log_sleep_calculation_details(sleep_metrics, chronotype_context, input_data)
        return sleep_metrics
    except Exception as err:
        logger.error(f"Sleep calculation error: {err}", exc_info=True)
        return _create_default_sleep_metrics()


def _parse_preferred_wake_time(
    prefs: dict
) -> Optional[time]:
    """
    Parses preferred wake time from preferences.
    
    Educational Note:
        ISO format parsing ensures consistent time handling across
        different time zones and client implementations.
    """
    wake_str = prefs.get("preferred_wake_time")
    if not wake_str:
        logger.info("ℹ️  No preferred_wake_time in preferences - will use chronotype default")
        return None
    
    logger.info(f"ℹ️  Found preferred_wake_time in preferences: {wake_str}")
    try:
        parsed_time = time.fromisoformat(wake_str)
        logger.info(f"✅ Parsed preferred_wake_time: {parsed_time.strftime('%H:%M')}")
        return parsed_time
    except ValueError:
        logger.warning(f"Invalid preferred_wake_time format: {wake_str}")
        return None


def _calculate_with_preferences(
    sleep_calculator: "SleepCalculator",
    chronotype_context: "ScheduleChronotypeContext",
    input_data: "ScheduleInputData",
    prefs: dict,
    target_wake: Optional[time]
) -> SleepMetrics:
    """
    Calculates sleep metrics with user preferences applied.
    
    Educational Note:
        Delegates to SleepCalculator which handles age-based duration,
        chronotype-based timing using simplified enum-based API.
        Sleep need can come from user_profile_data (string) or
        preferences (scale 0-100).
    """
    user_profile_data = input_data.user_profile_data or {}
    age = user_profile_data.get("age", 30)
    
    sleep_need_str = user_profile_data.get("sleep_need")
    if sleep_need_str:
        sleep_need = _convert_string_to_sleep_need(sleep_need_str)
    else:
        sleep_need_scale = prefs.get("sleep_need_scale")
        sleep_need = _convert_scale_to_sleep_need(sleep_need_scale)
    
    sleep_metrics = sleep_calculator.calculate_sleep_window(
        age=age,
        chronotype=chronotype_context.chronotype,
        sleep_need=sleep_need,
        target_wake_time=target_wake,
    )
    
    sleep_metrics = _adjust_wake_time_for_work_conflicts(sleep_metrics, prefs)
    return sleep_metrics


def _adjust_wake_time_for_work_conflicts(
    sleep_metrics: SleepMetrics,
    prefs: dict
) -> SleepMetrics:
    """
    Adjusts wake time if work starts before calculated wake time.
    
    Educational Note:
        Prevents INFEASIBLE schedules when chronotype wake time
        conflicts with work schedule. Prioritizes work commitments
        over ideal sleep timing.
    """
    logger.info("🔍 Checking for work conflicts with wake time...")
    work_prefs = prefs.get("work", {})
    work_start_str = work_prefs.get("start_time")
    
    logger.info(f"   work_prefs: {work_prefs}")
    logger.info(f"   work_start_str: {work_start_str}")
    
    if not work_start_str:
        logger.info("   No work start_time found, skipping adjustment")
        return sleep_metrics
    
    try:
        work_start = time.fromisoformat(work_start_str)
        wake_time = sleep_metrics.ideal_wake_time
        
        if work_start < wake_time:
            commute_min = work_prefs.get("commute_minutes", 0)
            required_wake = (datetime.combine(datetime.today(), work_start) - 
                           timedelta(minutes=commute_min + 30)).time()
            
            logger.warning(
                f"⚠️ Work conflict: work={work_start.strftime('%H:%M')} < "
                f"wake={wake_time.strftime('%H:%M')}. "
                f"Adjusting wake to {required_wake.strftime('%H:%M')}"
            )
            
            duration = sleep_metrics.ideal_duration
            new_bedtime = (datetime.combine(datetime.today(), required_wake) - 
                         duration).time()
            
            return SleepMetrics(
                ideal_duration=duration,
                ideal_bedtime=new_bedtime,
                ideal_wake_time=required_wake
            )
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not adjust wake time: {e}")
    
    return sleep_metrics


def _create_default_sleep_metrics() -> SleepMetrics:
    """
    Creates default sleep metrics as fallback.
    
    Educational Note:
        8-hour duration with 11pm-7am window represents population
        average, ensuring reasonable schedule even when personalized
        calculation fails.
    """
    return SleepMetrics(
        ideal_duration=timedelta(hours=8),
        ideal_bedtime=time(23, 0),
        ideal_wake_time=time(7, 0),
    )


def _log_sleep_calculation_details(
    sleep_metrics: "SleepMetrics",
    chronotype_context: "ScheduleChronotypeContext",
    input_data: "ScheduleInputData"
) -> None:
    """
    Logs detailed sleep calculation information for debugging.
    
    Educational Note:
        Provides transparency into sleep window calculation,
        making it easier to verify that chronotype and preferences
        are being correctly applied.
    """
    user_profile_data = input_data.user_profile_data or {}
    age = user_profile_data.get("age", 30)
    sleep_need = user_profile_data.get("sleep_need", "medium")
    
    duration_hours = sleep_metrics.ideal_duration.total_seconds() / 3600
    
    logger.info(
        f"🛏️  SLEEP WINDOW CALCULATED:\n"
        f"   Chronotype: {chronotype_context.chronotype.value}\n"
        f"   Age: {age}\n"
        f"   Sleep Need: {sleep_need}\n"
        f"   ⏰ Bedtime: {sleep_metrics.ideal_bedtime.strftime('%H:%M')}\n"
        f"   ⏰ Wake Time: {sleep_metrics.ideal_wake_time.strftime('%H:%M')}\n"
        f"   📊 Duration: {duration_hours:.1f}h"
    )
