"""
Sleep block merger for cross-midnight consolidation.

This module provides utilities to merge split sleep blocks that cross
midnight boundary into single continuous blocks for better UX. When sleep
spans from 23:45 to 06:00, it appears as two blocks (23:45-00:00 and
00:00-06:00) which should be merged for display purposes.

Educational Note:
    Midnight-crossing events are common in scheduling systems. This
    merger demonstrates how to handle boundary conditions elegantly
    while preserving data integrity and user comprehension.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def merge_sleep_blocks(schedule_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merges adjacent sleep blocks crossing midnight into single blocks.
    
    Identifies sleep blocks at day boundaries (end of day + start of
    next day) and combines them into unified representations with
    next_day indicator for proper time display.
    
    Args:
        schedule_items: Raw schedule items potentially with split sleep
        
    Returns:
        Schedule items with merged sleep blocks
        
    Educational Note:
        Post-processing scheduled output improves UX without affecting
        core solver logic, maintaining separation of concerns between
        optimization and presentation layers.
    """
    logger.info(f"🔄 Sleep merger: Processing {len(schedule_items)} items")
    
    if not schedule_items:
        return schedule_items
        
    sleep_items = [item for item in schedule_items if item.get("type") == "sleep"]
    logger.info(f"🔄 Found {len(sleep_items)} sleep items")
    for idx, sleep in enumerate(sleep_items, 1):
        logger.info(f"   Sleep {idx}: {sleep.get('start_time')} → {sleep.get('end_time')}")
        
    late_night = None
    morning = None
    
    for item in schedule_items:
        if _is_late_night_sleep(item):
            late_night = item
            logger.info(f"🌙 Found late night sleep: {item.get('start_time')} → {item.get('end_time')}")
        elif item.get("type") == "sleep" and item.get("start_time") == "00:00":
            morning = item
            logger.info(f"🌙 Found morning sleep: {item.get('start_time')} → {item.get('end_time')}")
    
    if late_night and morning:
        logger.info("✅ Found both blocks - merging")
        merged = _create_merged_sleep_block(late_night, morning)
        logger.info(f"✅ Merged sleep: {merged.get('start_time')} → {merged.get('end_time')} (next_day: {merged.get('end_time_next_day')})")
        
        result = []
        for item in schedule_items:
            if item is not late_night and item is not morning:
                result.append(item)
        result.append(merged)
        result.sort(key=lambda x: _time_to_sort_key(x.get("start_time", "")))
        logger.info(f"🔄 Sleep merger: Returning {len(result)} items after merge")
        return result
    else:
        logger.info("⚠️ No matching pair found for merge")
        return schedule_items


def _is_late_night_sleep(item: Dict[str, Any]) -> bool:
    """
    Checks if item is sleep block starting late evening.
    
    Identifies sleep blocks that start after 22:00 and likely
    cross midnight, indicating potential merge candidates.
    """
    if item.get("type") != "sleep":
        return False
        
    start = item.get("start_time", "")
    return start >= "22:00"


def _find_next_morning_sleep(items: List[Dict[str, Any]], current_idx: int) -> Dict[str, Any]:
    """
    Finds matching morning sleep block after late night sleep.
    
    Searches for sleep block starting at 00:00 immediately
    following the late night sleep, indicating continuation
    of same sleep period across midnight.
    """
    if current_idx + 1 >= len(items):
        return None
        
    next_item = items[current_idx + 1]
    
    if next_item.get("type") != "sleep":
        return None
        
    if next_item.get("start_time") == "00:00":
        return next_item
        
    return None


def _create_merged_sleep_block(
    late_night: Dict[str, Any],
    morning: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Creates single sleep block from midnight-crossing pair.
    
    Combines two sleep blocks into one with extended end_time
    and next_day indicator showing sleep extends into next day.
    Preserves all metadata from original blocks.
    
    Educational Note:
        The merged block uses bedtime as start (from previous day)
        and wake time as end (current day), with start_time_previous_day
        flag to indicate cross-midnight behavior for UI rendering.
    """
    return {
        "type": "sleep",
        "name": "Sleep",
        "start_time": late_night.get("start_time"),
        "end_time": morning.get("end_time"),
        "start_time_previous_day": True,
        "duration_hours": _calculate_cross_midnight_duration(
            late_night.get("start_time", "00:00"),
            morning.get("end_time", "00:00")
        ),
        "description": f"Sleep from {late_night.get('start_time')} (previous day) to {morning.get('end_time')} (current day)"
    }


def _calculate_cross_midnight_duration(start: str, end: str) -> float:
    """
    Calculates sleep duration spanning midnight boundary.
    
    Computes total hours from evening start time through
    midnight into morning end time. Handles HH:MM format.
    """
    start_hour, start_min = _parse_time(start)
    end_hour, end_min = _parse_time(end)
    
    minutes_to_midnight = (24 - start_hour) * 60 - start_min
    minutes_after_midnight = end_hour * 60 + end_min
    
    total_minutes = minutes_to_midnight + minutes_after_midnight
    return round(total_minutes / 60, 2)


def _parse_time(time_str: str) -> tuple:
    """
    Parses HH:MM time string to hour and minute integers.
    
    Extracts numeric components from time string for
    duration calculations. Returns (0, 0) for invalid input.
    """
    try:
        parts = time_str.split(":")
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError, AttributeError):
        return 0, 0


def _time_to_sort_key(time_str: str) -> int:
    """
    Converts HH:MM time string to sortable integer minutes.
    
    Educational Note:
        Enables chronological sorting of schedule items by converting
        time strings to numeric values. Essential for maintaining proper
        order after merging sleep blocks.
    """
    try:
        hours, minutes = _parse_time(time_str)
        return hours * 60 + minutes
    except Exception:
        return 0
