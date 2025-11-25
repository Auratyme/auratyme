"""
Schedule gap filling with breaks.

This module fills time gaps between scheduled items with appropriate
break types to create a complete 24-hour schedule.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from src.utils.time_utils import total_minutes_to_time

logger = logging.getLogger(__name__)


def fill_schedule_gaps_with_breaks(
    blocks: List[Tuple[int, int, Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """
    Fills gaps between scheduled blocks with appropriate break types.
    
    Educational Note:
        Ensures complete 24-hour schedule with no unaccounted time.
        Break type determined by gap duration for contextual labeling.
        
        Handles sleep blocks specially:
        - Sleep defines the day boundaries (wake time to bedtime)
        - Active hours fill the gap between wake and bed
        - Breaks fill any gaps between activities
        - Sleep appears last in the display for intuitive reading
    """
    final_schedule = []
    
    sleep_blocks, active_blocks = _separate_sleep_from_blocks(blocks)
    
    if sleep_blocks:
        _build_continuous_schedule_with_sleep(
            final_schedule, active_blocks, sleep_blocks
        )
    else:
        _build_continuous_schedule_without_sleep(
            final_schedule, active_blocks
        )
    
    return final_schedule


def _separate_sleep_from_blocks(
    blocks: List[Tuple[int, int, Dict[str, Any]]]
) -> Tuple[List[Tuple[int, int, Dict[str, Any]]], List[Tuple[int, int, Dict[str, Any]]]]:
    """
    Separates sleep blocks from active blocks.
    
    Educational Note:
        Sleep gets special handling as it defines day boundaries.
        TWO sleep blocks expected: morning (00:00-wake) and evening (bed-24:00).
        All other blocks are processed sequentially with gap filling
        to create a continuous schedule from wake to sleep.
    """
    sleep_blocks = []
    active_blocks = []
    
    for start, end, meta in blocks:
        if meta.get("type") == "sleep":
            sleep_blocks.append((start, end, meta))
        else:
            active_blocks.append((start, end, meta))
    
    active_blocks.sort(key=lambda x: x[0])
    sleep_blocks.sort(key=lambda x: x[0])
    return sleep_blocks, active_blocks


def _build_continuous_schedule_with_sleep(
    final_schedule: List[Dict[str, Any]],
    active_blocks: List[Tuple[int, int, Dict[str, Any]]],
    sleep_blocks: List[Tuple[int, int, Dict[str, Any]]]
) -> None:
    """
    Builds continuous schedule with TWO sleep blocks.
    
    Educational Note:
        Handles TWO sleep blocks representing split sleep:
        - Morning block: 00:00 to wake time (previous night's sleep ending)
        - Evening block: bedtime to 24:00 (tonight's sleep starting)
        
        Creates natural flow: Morning Sleep → Wake → Activities/Breaks → Bedtime → Evening Sleep
        
        Both sleep blocks are added to final schedule in chronological order.
    """
    morning_sleep = None
    evening_sleep = None
    
    for start, end, meta in sleep_blocks:
        if meta.get("event_id") == "sleep_previous_night":
            morning_sleep = (start, end, meta)
        elif meta.get("event_id") == "sleep_upcoming_night":
            evening_sleep = (start, end, meta)
    
    if morning_sleep:
        final_schedule.append(morning_sleep[2])
        wake_min = morning_sleep[1]
    else:
        wake_min = 0
    
    if evening_sleep:
        bed_min = evening_sleep[0]
    else:
        bed_min = 1440
    
    prev_end = wake_min
    
    for start, end, meta in active_blocks:
        if start >= wake_min and start < bed_min:
            if start > prev_end:
                add_gap_break(final_schedule, prev_end, start)
            final_schedule.append(meta)
            prev_end = end
    
    if prev_end < bed_min:
        add_gap_break(final_schedule, prev_end, bed_min)
    
    if evening_sleep:
        final_schedule.append(evening_sleep[2])


def _build_continuous_schedule_without_sleep(
    final_schedule: List[Dict[str, Any]],
    active_blocks: List[Tuple[int, int, Dict[str, Any]]]
) -> None:
    """
    Builds continuous schedule for full 24 hours without sleep.
    
    Educational Note:
        Fallback for when no sleep is scheduled.
        Fills entire day from 00:00 to 24:00 with activities
        and breaks, ensuring complete time coverage.
    """
    prev_end = 0
    
    for start, end, meta in active_blocks:
        if start > prev_end:
            add_gap_break(final_schedule, prev_end, start)
        final_schedule.append(meta)
        prev_end = end
    
    if prev_end < 1440:
        add_end_of_day_break(final_schedule, prev_end)


def add_gap_break(
    schedule: List[Dict[str, Any]],
    prev_end: int,
    next_start: int
) -> None:
    """
    Adds break to fill gap between scheduled items.
    
    Educational Note:
        Fills ALL gaps >= 1 minute to ensure complete schedule.
        Even tiny 1-minute gaps get Short Break to show continuous timeline.
    """
    gap_duration = next_start - prev_end
    
    if gap_duration < 1:
        return
    
    break_name, break_type = determine_break_type_by_duration(gap_duration)
    
    schedule.append({
        "type": break_type,
        "name": break_name,
        "start_time": total_minutes_to_time(prev_end).strftime("%H:%M"),
        "end_time": total_minutes_to_time(next_start).strftime("%H:%M"),
        "duration_minutes": gap_duration,
    })


def determine_break_type_by_duration(
    duration: int
) -> Tuple[str, str]:
    """
    Determines break name and type based on duration.
    
    Educational Note:
        Longer gaps = more substantial break types:
        45+ min = Free Time, 15-45 = Short Break, <15 = Quick Break.
    """
    if duration >= 45:
        return ("Free Time", "free_time")
    
    if duration >= 15:
        return ("Short Break", "short_break")
    
    return ("Quick Break", "quick_break")


def add_end_of_day_break(
    schedule: List[Dict[str, Any]],
    prev_end: int
) -> None:
    """
    Adds final break from last scheduled item to midnight.
    
    Educational Note:
        Ensures schedule covers full 24 hours. Duration determines
        whether it's quick break or free time.
    """
    gap_duration = 1440 - prev_end
    
    if gap_duration <= 30:
        break_name, break_type = "Quick Break", "quick_break"
    else:
        break_name, break_type = "Free Time", "free_time"
    
    schedule.append({
        "type": break_type,
        "name": break_name,
        "start_time": total_minutes_to_time(prev_end).strftime("%H:%M"),
        "end_time": "00:00",  # Midnight of next day, but display as 00:00 since it's end of current day
        "duration_minutes": gap_duration,
    })
