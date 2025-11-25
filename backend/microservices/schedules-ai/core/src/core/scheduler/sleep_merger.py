"""
Sleep block merging for display purposes.

This module merges separate sleep window blocks into a single continuous
sleep block for better user experience and schedule readability.
"""

import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


def merge_sleep_blocks(
    blocks: List[Tuple[int, int, Dict[str, Any]]],
    sleep_metrics=None
) -> List[Tuple[int, int, Dict[str, Any]]]:
    """
    Converts sleep blocks to TWO distinct blocks with next_day flag.
    
    Educational Note:
        Daily schedule needs TWO sleep blocks:
        1. Previous night sleep (ending today morning) with next_day=True
        2. Tonight's sleep (starting today evening) with next_day=True
        
        Both blocks cross midnight naturally, representing realistic
        sleep patterns where sleep starts one day and ends the next.
    
    Args:
        blocks: List of (start_min, end_min, metadata) tuples
        sleep_metrics: Optional SleepMetrics with bedtime/wake_time for display
        
    Returns:
        New list with TWO separate sleep blocks, each with next_day=True
    """
    previous_sleep = None
    upcoming_sleep = None
    other_blocks = []
    
    for start, end, meta in blocks:
        event_id = meta.get("event_id", "")
        
        if event_id == "sleep_previous_night":
            previous_sleep = (start, end, meta)
        elif event_id == "sleep_upcoming_night":
            upcoming_sleep = (start, end, meta)
        else:
            other_blocks.append((start, end, meta))
    
    if previous_sleep and sleep_metrics:
        other_blocks.append(_create_full_previous_sleep_block(previous_sleep, sleep_metrics))
    elif previous_sleep:
        other_blocks.append(_create_sleep_block_as_type_sleep(previous_sleep, "sleep_previous_night"))
        
    if upcoming_sleep and sleep_metrics:
        other_blocks.append(_create_full_upcoming_sleep_block(upcoming_sleep, sleep_metrics))
    elif upcoming_sleep:
        other_blocks.append(_create_sleep_block_as_type_sleep(upcoming_sleep, "sleep_upcoming_night"))
    
    other_blocks.sort(key=lambda x: x[0])
    return other_blocks


def _create_sleep_block_as_type_sleep(
    sleep_tuple: Tuple[int, int, Dict[str, Any]],
    event_id: str
) -> Tuple[int, int, Dict[str, Any]]:
    """
    Converts fixed_event sleep block to type=sleep without changing times.
    
    Educational Note:
        Simply changes type from fixed_event to sleep, preserving
        original start/end times. sleep_corrector will merge them later.
    """
    from src.utils.time_utils import total_minutes_to_time
    
    start_min, end_min, meta = sleep_tuple
    start_time_obj = total_minutes_to_time(start_min)
    end_time_obj = total_minutes_to_time(end_min)
    
    return (
        start_min,
        end_min,
        {
            "type": "sleep",
            "event_id": event_id,
            "name": "Sleep",
            "start_time": start_time_obj.strftime("%H:%M"),
            "end_time": end_time_obj.strftime("%H:%M"),
            "duration_minutes": end_min - start_min,
            "description": f"Sleep block {event_id}"
        }
    )


def _create_morning_sleep_block(
    sleep_tuple: Tuple[int, int, Dict[str, Any]]
) -> Tuple[int, int, Dict[str, Any]]:
    """
    Creates morning sleep block (00:00-wake_time).
    
    Educational Note:
        This represents the portion of sleep that occurs after midnight
        on the current day. Always starts at 0 and ends at wake time.
    """
    start_min, end_min, meta = sleep_tuple
    from src.utils.time_utils import total_minutes_to_time
    
    wake_min = end_min
    
    return (
        start_min,
        wake_min,
        {
            "type": "sleep",
            "event_id": "sleep_previous_night",
            "name": "Sleep",
            "start_time": "00:00",
            "end_time": total_minutes_to_time(wake_min).strftime("%H:%M"),
            "duration_minutes": wake_min,
            "next_day": False,
            "description": "Morning sleep portion"
        }
    )


def _create_evening_sleep_block(
    sleep_tuple: Tuple[int, int, Dict[str, Any]]
) -> Tuple[int, int, Dict[str, Any]]:
    """
    Creates evening sleep block (bedtime-24:00).
    
    Educational Note:
        This represents the portion of sleep that occurs before midnight
        on the current day. Starts at bedtime and ends at 1440 (24:00).
    """
    start_min, end_min, meta = sleep_tuple
    from src.utils.time_utils import total_minutes_to_time
    
    bed_min = start_min
    
    return (
        bed_min,
        1440,
        {
            "type": "sleep",
            "event_id": "sleep_upcoming_night",
            "name": "Sleep",
            "start_time": total_minutes_to_time(bed_min).strftime("%H:%M"),
            "end_time": "24:00",
            "duration_minutes": 1440 - bed_min,
            "next_day": False,
            "description": "Evening sleep portion"
        }
    )


def _create_sleep_block_with_next_day(
    sleep_tuple: Tuple[int, int, Dict[str, Any]],
    description: str
) -> Tuple[int, int, Dict[str, Any]]:
    """
    Creates sleep block with next_day flag for midnight crossing.
    
    Educational Note:
        Sleep blocks crossing midnight need next_day=True flag
        to indicate end_time is on following day. This prevents
        confusion when displaying 23:45-06:00 (where 06:00 is next day).
        
        Extracts bedtime/wake time from metadata which contains
        actual sleep preferences from sleep_metrics.
    
    Args:
        sleep_tuple: (start_min, end_min, meta) for sleep window
        description: Human-readable description
        
    Returns:
        Sleep block tuple with next_day flag and proper timing
    """
    start_min, end_min, meta = sleep_tuple
    from src.utils.time_utils import total_minutes_to_time
    
    event_id = meta.get("event_id", "")
    
    if event_id == "sleep_previous_night":
        wake_min = end_min
        bed_min = meta.get("ideal_bedtime_minutes", 23 * 60 + 30)
        
        if bed_min >= 1440:
            bed_min = 23 * 60 + 30
        
        sleep_duration = (1440 - bed_min) + wake_min
        
        return (
            start_min,
            wake_min + 1440,
            {
                "type": "sleep",
                "event_id": event_id,
                "name": "Sleep",
                "start_time": total_minutes_to_time(bed_min).strftime("%H:%M"),
                "end_time": total_minutes_to_time(wake_min).strftime("%H:%M"),
                "duration_minutes": sleep_duration,
                "next_day": True,
                "description": description
            }
        )
    else:
        bed_min = start_min
        wake_min = meta.get("ideal_wake_minutes", 7 * 60)
        
        if wake_min >= 1440:
            wake_min = wake_min - 1440
        
        sleep_duration = (1440 - bed_min) + wake_min
        
        return (
            bed_min,
            end_min,
            {
                "type": "sleep",
                "event_id": event_id,
                "name": "Sleep",
                "start_time": total_minutes_to_time(bed_min).strftime("%H:%M"),
                "end_time": total_minutes_to_time(wake_min).strftime("%H:%M"),
                "duration_minutes": sleep_duration,
                "next_day": True,
                "description": description
            }
        )


def _create_full_previous_sleep_block(
    sleep_tuple: Tuple[int, int, Dict[str, Any]],
    sleep_metrics
) -> Tuple[int, int, Dict[str, Any]]:
    """
    Creates previous night sleep block with full sleep window display.
    
    Educational Note:
        Shows complete sleep pattern (e.g., 22:30-06:00) at START of day.
        Represents sleep from previous evening that ended this morning.
        Block positioned at start (minute 0) but displays full sleep time.
    """
    from src.utils.time_utils import time_to_total_minutes
    
    _, wake_min, meta = sleep_tuple
    
    bedtime_str = sleep_metrics.ideal_bedtime.strftime("%H:%M")
    wake_str = sleep_metrics.ideal_wake_time.strftime("%H:%M")
    bed_min = time_to_total_minutes(sleep_metrics.ideal_bedtime)
    
    return (
        0,
        wake_min,
        {
            "type": "sleep",
            "event_id": "sleep_previous_night",
            "name": "Sleep",
            "start_time": bedtime_str,
            "end_time": wake_str,
            "end_time_next_day": True,
            "duration_minutes": wake_min + (1440 - bed_min),
            "description": f"Sleep {bedtime_str}-{wake_str}"
        }
    )


def _create_full_upcoming_sleep_block(
    sleep_tuple: Tuple[int, int, Dict[str, Any]],
    sleep_metrics
) -> Tuple[int, int, Dict[str, Any]]:
    """
    Creates upcoming night sleep block with full sleep window display.
    
    Educational Note:
        Shows complete sleep pattern (e.g., 22:30-06:00) at END of day.
        Represents tonight's sleep that will continue tomorrow morning.
        Block positioned at end (bedtime minute) but displays full sleep time.
        IDENTICAL time display to previous_night - same sleep pattern.
    """
    from src.utils.time_utils import time_to_total_minutes
    
    bed_min, _, meta = sleep_tuple
    
    bedtime_str = sleep_metrics.ideal_bedtime.strftime("%H:%M")
    wake_str = sleep_metrics.ideal_wake_time.strftime("%H:%M")
    wake_min = time_to_total_minutes(sleep_metrics.ideal_wake_time)
    
    return (
        bed_min,
        1440,
        {
            "type": "sleep",
            "event_id": "sleep_upcoming_night",
            "name": "Sleep",
            "start_time": bedtime_str,
            "end_time": wake_str,
            "end_time_next_day": True,
            "duration_minutes": wake_min + (1440 - bed_min),
            "description": f"Sleep {bedtime_str}-{wake_str}"
        }
    )

