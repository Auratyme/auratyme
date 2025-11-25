"""
Time validation and correction utilities for schedule data.

Ensures that schedule times are in valid HH:MM format and can
be displayed properly. Handles edge cases where times might be
malformed or represent next-day timeslots.
"""

import logging
import re
from typing import Tuple, Optional
from datetime import time as datetime_time

logger = logging.getLogger(__name__)


def time_object_to_string(t) -> Optional[str]:
    """
    Converts time object (datetime.time or string) to HH:MM string.
    
    Args:
        t: Can be datetime.time object, string, or other
        
    Returns:
        HH:MM format string or None if invalid
    """
    if isinstance(t, datetime_time):
        return t.strftime("%H:%M")
    if isinstance(t, str):
        return t
    if hasattr(t, 'strftime'):
        return t.strftime("%H:%M")
    return None


def validate_and_fix_time_format(time_str: str) -> Optional[str]:
    """
    Validates and fixes time format to HH:MM.
    
    Args:
        time_str: Time string that may be in various formats
        
    Returns:
        Valid HH:MM format string, or None if invalid
    """
    if not time_str or not isinstance(time_str, str):
        return None
    
    time_str = time_str.strip()
    
    # Handle HH:MM:SS -> HH:MM
    if time_str.count(':') == 2:
        parts = time_str.split(':')
        try:
            hour = int(parts[0])
            minute = int(parts[1])
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"
        except (ValueError, IndexError):
            pass
    
    # Handle HH:MM
    elif time_str.count(':') == 1:
        parts = time_str.split(':')
        try:
            hour = int(parts[0])
            minute = int(parts[1])
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"
        except (ValueError, IndexError):
            pass
    
    logger.warning(f"❌ Invalid time format: '{time_str}'")
    return None


def time_to_minutes(time_str: str) -> int:
    """Converts HH:MM to minutes since midnight."""
    try:
        validated = validate_and_fix_time_format(time_str)
        if not validated:
            return -1
        parts = validated.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        return hours * 60 + minutes
    except Exception as e:
        logger.error(f"Error converting time to minutes: {e}")
        return -1


def validate_schedule_item(item: dict) -> Tuple[bool, Optional[str]]:
    """
    Validates a single schedule item for time consistency.
    
    Args:
        item: Schedule item dict with start_time, end_time, task
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(item, dict):
        return False, "Item is not a dictionary"
    
    st = item.get("start_time")
    et = item.get("end_time")
    task = item.get("task", "Unknown")
    
    if not st or not et:
        return False, f"Task '{task}' missing times (start={st}, end={et})"
    
    st_valid = validate_and_fix_time_format(st)
    et_valid = validate_and_fix_time_format(et)
    
    if not st_valid:
        return False, f"Task '{task}' has invalid start_time: '{st}'"
    
    if not et_valid:
        return False, f"Task '{task}' has invalid end_time: '{et}'"
    
    st_min = time_to_minutes(st_valid)
    et_min = time_to_minutes(et_valid)
    
    if st_min < 0 or et_min < 0:
        return False, f"Task '{task}' has invalid time values"
    
    return True, None


def repair_schedule_data(schedule_data: dict) -> dict:
    """
    Attempts to repair schedule data by fixing time formats.
    
    Handles Pydantic model objects (SimplifiedScheduleTask) by
    converting them to dicts, and fixes time formats.
    
    Args:
        schedule_data: Dict with tasks list
        
    Returns:
        Repaired schedule data with fixed times
    """
    if not isinstance(schedule_data, dict):
        logger.warning("Schedule data is not a dict, returning as-is")
        return schedule_data
    
    tasks = schedule_data.get("tasks", [])
    if not isinstance(tasks, list):
        logger.warning(f"Tasks is not a list (type={type(tasks)}), returning as-is")
        return schedule_data
    
    logger.info(f"🔧 Attempting to repair {len(tasks)} tasks...")
    repaired_tasks = []
    skipped = 0
    
    for idx, item in enumerate(tasks):
        # Convert Pydantic models to dict
        if hasattr(item, 'dict'):
            item = item.dict()
        elif hasattr(item, '__dict__') and not isinstance(item, dict):
            item = item.__dict__
        
        if not isinstance(item, dict):
            logger.warning(f"   Task {idx} is not convertible to dict (type={type(item)}), skipping")
            skipped += 1
            continue
        
        st = item.get("start_time")
        et = item.get("end_time")
        task_name = item.get("task", f"Task {idx}")
        
        # Convert time objects to strings
        st = time_object_to_string(st) if st else None
        et = time_object_to_string(et) if et else None
        
        st_fixed = validate_and_fix_time_format(st)
        et_fixed = validate_and_fix_time_format(et)
        
        if not st_fixed or not et_fixed:
            logger.warning(f"   Task '{task_name}' has invalid times: {st} → {et}, skipping")
            skipped += 1
            continue
        
        # Create repaired item
        repaired = item.copy()
        repaired["start_time"] = st_fixed
        repaired["end_time"] = et_fixed
        repaired_tasks.append(repaired)
        logger.info(f"   ✅ Fixed task '{task_name}': {st} → {st_fixed}, {et} → {et_fixed}")
    
    logger.info(f"🎯 Repair result: {len(repaired_tasks)} valid, {skipped} skipped")
    
    return {
        **schedule_data,
        "tasks": repaired_tasks
    }
