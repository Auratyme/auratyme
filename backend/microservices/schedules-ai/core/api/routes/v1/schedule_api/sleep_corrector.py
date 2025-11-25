"""
Sleep block corrector for LLM-generated schedules.

This module fixes sleep blocks in LLM output to match actual sleep
recommendation data. Creates TWO full sleep blocks (previous night
and upcoming night) crossing midnight with proper routines.

Educational Note:
    Daily schedule needs TWO sleep blocks:
    1. Previous night sleep ending in today's morning
    2. Today's night sleep starting in today's evening
    Morning routine follows wake, evening routine precedes sleep.
"""

import logging
from datetime import datetime, time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _fill_free_time_gaps(
    items: List[Dict[str, Any]],
    day_start: int = 0,
    day_end: int = 1440
) -> List[Dict[str, Any]]:
    """
    Fills gaps between schedule items with Free Time blocks.
    
    CRITICAL: Sleep blocks are excluded from gap analysis and preserved
    as-is, since they have special priority in final sorting.
    
    Educational Note:
        After LLM generates schedule, there may be gaps between
        activities. These gaps represent unscheduled time where
        user has freedom to choose activities.
        
        For late bedtime scenarios (bed 01:00, wake 07:00):
        - Sleep block (01:00-07:00) is preserved separately
        - Gap analysis only considers non-sleep items (07:00-01:00)
        - Free Time fills gap from last task (20:45) to evening routine (00:15)
    """
    if not items:
        return [{
            "type": "free_time",
            "name": "Free Time",
            "start_time": _minutes_to_time(day_start),
            "end_time": _minutes_to_time(day_end)
        }]
    
    sleep_items = [item for item in items if item.get("type") == "sleep"]
    non_sleep_items = [item for item in items if item.get("type") != "sleep"]
    
    sorted_items = sorted(non_sleep_items, key=lambda x: _time_to_minutes(x.get("start_time", "00:00")))
    result = []
    current_time = day_start
    
    for item in sorted_items:
        item_start = _time_to_minutes(item.get("start_time", "00:00"))
        item_end = _time_to_minutes(item.get("end_time", "00:00"))
        
        if item_start > current_time:
            gap_duration = item_start - current_time
            if gap_duration >= 5:
                result.append({
                    "type": "free_time",
                    "name": "Free Time",
                    "start_time": _minutes_to_time(current_time),
                    "end_time": _minutes_to_time(item_start),
                    "duration_minutes": gap_duration
                })
        
        result.append(item)
        current_time = max(current_time, item_end)
    
    if current_time < day_end:
        gap_duration = day_end - current_time
        if gap_duration >= 5:
            result.append({
                "type": "free_time",
                "name": "Free Time",
                "start_time": _minutes_to_time(current_time),
                "end_time": _minutes_to_time(day_end),
                "duration_minutes": gap_duration
            })
    
    result.extend(sleep_items)
    return result


def correct_sleep_blocks(
    schedule_items: List[Dict[str, Any]],
    sleep_recommendation: Optional[Any],
    routine_preferences: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Corrects sleep and routine blocks for full daily schedule.
    
    Creates TWO continuous sleep blocks crossing midnight:
    - Previous night sleep → Morning routine (start of day)
    - Evening routine → Tonight's sleep (end of day)
    
    Args:
        schedule_items: LLM-generated schedule items
        sleep_recommendation: SleepMetrics with ideal bedtime/wake time
        routine_preferences: Dict with morning/evening routine durations
        
    Returns:
        Schedule with corrected sleep and routine blocks
        
    Educational Note:
        Daily schedule spans ~3 days via sleep blocks:
        Previous night sleep → Today's activities → Tonight's sleep
        This represents realistic daily schedule boundaries.
    """
    if not sleep_recommendation:
        logger.warning("No sleep recommendation provided - skipping correction")
        return schedule_items
        
    bedtime = sleep_recommendation.ideal_bedtime
    wake_time = sleep_recommendation.ideal_wake_time
    wake_minutes = _time_to_minutes(wake_time.strftime("%H:%M"))
    bedtime_minutes = _time_to_minutes(bedtime.strftime("%H:%M"))
    is_late_bedtime = bedtime_minutes < wake_minutes
    
    sleep_blocks_from_solver = [
        item for item in schedule_items
        if item.get("type") == "sleep" and item.get("event_id") in ["sleep_previous_night", "sleep_upcoming_night"]
    ]
    
    sleep_blocks_from_llm = [
        item for item in schedule_items
        if item.get("type") == "sleep" and item.get("event_id") not in ["sleep_previous_night", "sleep_upcoming_night"]
    ]
    
    if len(sleep_blocks_from_solver) == 2:
        logger.info("✅ Found 2 solver sleep blocks - creating TWO FULL 9-hour sleep cycles for display")
        return _create_two_separate_sleep_blocks(
            schedule_items, sleep_blocks_from_solver, routine_preferences, bedtime, wake_time
        )
    elif len(sleep_blocks_from_solver) == 1:
        previous = next((b for b in sleep_blocks_from_solver if b.get("event_id") == "sleep_previous_night"), None)
        if previous:
            logger.info("✅ Found 1 solver sleep block (previous_night only) - creating TWO FULL 9-hour sleep cycles")
            logger.info(f"🔍 DEBUG: Total items before correction: {len(schedule_items)}")
            logger.info(f"🔍 DEBUG: Items with 'routine' in name/event_id:")
            for item in schedule_items:
                if "routine" in item.get("name", "").lower() or "routine" in item.get("event_id", "").lower():
                    logger.info(f"   - {item.get('name')} ({item.get('start_time')}-{item.get('end_time')}), type={item.get('type')}, event_id={item.get('event_id')}")
            result = _create_two_sleep_from_single_block(
                schedule_items, previous, routine_preferences, bedtime, wake_time
            )
            logger.info(f"🔍 DEBUG: Total items after correction: {len(result)}")
            logger.info(f"🔍 DEBUG: Items with 'routine' in name/event_id after correction:")
            for item in result:
                if "routine" in item.get("name", "").lower() or "routine" in item.get("event_id", "").lower():
                    logger.info(f"   - {item.get('name')} ({item.get('start_time')}-{item.get('end_time')}), type={item.get('type')}, event_id={item.get('event_id')}")
            return result
    elif len(sleep_blocks_from_llm) == 2:
        logger.info("✅ Found 2 LLM sleep blocks - converting to TWO FULL 9-hour sleep cycles for display")
        return _create_two_separate_sleep_blocks(
            schedule_items, sleep_blocks_from_llm, routine_preferences, bedtime, wake_time
        )
    
    llm_sleep_blocks = [item for item in schedule_items if item.get("type") == "sleep"]
    
    if is_late_bedtime and len(llm_sleep_blocks) > 1:
        logger.warning(f"⚠️ LATE BEDTIME ({bedtime.strftime('%H:%M')} < {wake_time.strftime('%H:%M')}): LLM incorrectly generated {len(llm_sleep_blocks)} sleep blocks, correcting to 1...")
    
    logger.info(f"🔧 Always applying correction to create FULL 9-hour sleep cycles (bedtime={bedtime.strftime('%H:%M')}, wake={wake_time.strftime('%H:%M')})")
    
    def should_keep_item(item):
        """
        Keeps items that are NOT sleep/routine (we'll add proper ones).
        
        CRITICAL FOR LATE BEDTIME:
        - Keep ONLY solver routines with correct event_id (morning_routine, evening_routine)
        - Remove LLM-generated routines (no event_id or wrong timing)
        
        Educational Note:
            LLM often generates evening routine at wrong time (e.g., 21:10-21:55)
            when it should be 00:15-01:00 for late bedtime. We must filter these out
            and keep only solver-generated routines with proper event_id markers.
        """
        item_type = item.get("type")
        event_id = item.get("event_id", "")
        name = item.get("name", "")
        
        if item_type == "fixed_event" and event_id in ["morning_routine", "evening_routine"]:
            return True
        
        return item_type not in ["sleep", "routine"]
    
    kept_items = [item for item in schedule_items if should_keep_item(item)]
    removed_count = len(schedule_items) - len(kept_items)
    
    if is_late_bedtime:
        logger.info(f"🌙 LATE BEDTIME CORRECTION: bed={bedtime.strftime('%H:%M')} < wake={wake_time.strftime('%H:%M')}")
        logger.info(f"   Removed {removed_count} incorrect sleep/routine blocks from LLM")
        
        logger.info(f"   🔍 Checking kept_items for Evening Routine:")
        for idx, item in enumerate(kept_items):
            logger.info(f"      [{idx}] type={item.get('type')}, name={item.get('name')}, event_id={item.get('event_id')}")
        
        has_evening_routine = any(
            item.get("type") == "fixed_event" and 
            (("evening" in item.get("event_id", "").lower() and "routine" in item.get("event_id", "").lower()) or
             ("evening" in item.get("name", "").lower() and "routine" in item.get("name", "").lower()))
            for item in kept_items
        )
        
        logger.info(f"   has_evening_routine check result: {has_evening_routine}")
        
        if not has_evening_routine:
            logger.info(f"   ⚠️ Evening Routine missing, adding it (00:15-01:00)")
            evening_duration = routine_preferences.get("evening_duration_minutes", 45) if routine_preferences else 45
            evening_start_min = _time_to_minutes(bedtime.strftime("%H:%M")) - evening_duration
            if evening_start_min < 0:
                evening_start_min += 1440
            
            evening_routine = {
                "type": "fixed_event",
                "event_id": "evening_routine",
                "name": "Evening Routine",
                "start_time": _minutes_to_time(evening_start_min),
                "end_time": bedtime.strftime("%H:%M"),
                "duration_minutes": evening_duration,
            }
            kept_items.append(evening_routine)
            evening_routine_start = _minutes_to_time(evening_start_min)
        else:
            evening_item = next((item for item in kept_items if item.get("type") == "fixed_event" and "evening" in item.get("name", "").lower() and "routine" in item.get("name", "").lower()), None)
            evening_routine_start = evening_item.get("start_time") if evening_item else "00:15"
        
        for item in kept_items:
            if item.get("type") == "free_time":
                old_end = item.get("end_time")
                item["end_time"] = evening_routine_start
                logger.info(f"   🔧 Fixed Free Time end_time: {old_end} → {evening_routine_start}")
        
        main_sleep_block = {
            "type": "sleep",
            "name": "Sleep",
            "start_time": bedtime.strftime("%H:%M"),
            "end_time": wake_time.strftime("%H:%M"),
            "end_time_next_day": False,
            "description": f"Sleep from {bedtime.strftime('%H:%M')} to {wake_time.strftime('%H:%M')} (current night)"
        }
        
        kept_items.append(main_sleep_block)
        
        upcoming_sleep_block = {
            "type": "sleep",
            "name": "Sleep",
            "start_time": bedtime.strftime("%H:%M"),
            "end_time": wake_time.strftime("%H:%M"),
            "end_time_next_day": True,
            "description": f"Upcoming sleep from {bedtime.strftime('%H:%M')} to {wake_time.strftime('%H:%M')} (next day)"
        }
        
        kept_items.append(upcoming_sleep_block)
        logger.info(f"   ✅ Added 2 sleep blocks: current night (01:00-07:00) + upcoming night (01:00-07:00 next day)")
        
        non_sleep_items = [item for item in kept_items if item.get("type") != "sleep"]
        sorted_non_sleep = sorted(non_sleep_items, key=lambda x: _time_to_minutes(x.get("start_time", "00:00")))
        
        last_task_end_time = None
        evening_routine_start_time = None
        
        for item in sorted_non_sleep:
            if "evening" in item.get("name", "").lower() and "routine" in item.get("name", "").lower():
                evening_routine_start_time = item.get("start_time")
                break
        
        for item in reversed(sorted_non_sleep):
            item_type = item.get("type", "")
            item_name = item.get("name", "").lower()
            if item_type in ["task", "fixed_event"] and "routine" not in item_name and "sleep" not in item_name:
                last_task_end_time = item.get("end_time")
                break
        
        if last_task_end_time and evening_routine_start_time:
            last_end_min = _time_to_minutes(last_task_end_time)
            evening_start_min = _time_to_minutes(evening_routine_start_time)
            
            if evening_start_min == 0:
                evening_start_min = 1440
            
            if evening_start_min > last_end_min:
                gap_duration = evening_start_min - last_end_min
                if gap_duration >= 5:
                    free_time_block = {
                        "type": "free_time",
                        "name": "Free Time",
                        "start_time": last_task_end_time,
                        "end_time": evening_routine_start_time,
                        "duration_minutes": gap_duration
                    }
                    kept_items.append(free_time_block)
                    logger.info(f"   ✅ Added single Free Time block: {last_task_end_time} → {evening_routine_start_time} ({gap_duration}min)")
        
        logger.info(f"   ✅ Total items after adding Free Time: {len(kept_items)}")
        
        bed_minutes_val = _time_to_minutes(bedtime.strftime("%H:%M"))
        wake_minutes_val = _time_to_minutes(wake_time.strftime("%H:%M"))
        
        def sort_key_late_bedtime(item):
            """
            Sorts for late bedtime with realistic daily structure.
            
            Order:
            1. Sleep current night (01:00-07:00) - priority 0 (FIRST)
            2. Morning routine (07:00-07:30) - priority by start_time
            3. Regular schedule (07:30-20:20) - priority by start_time
            4. Free Time crossing midnight (20:20-00:15) - priority 99997
            5. Evening routine (00:15-01:00) - priority 99998
            6. Sleep next night (01:00-07:00 next day) - priority 99999 (LAST)
            
            Educational Note:
                Shows FULL sleep cycle: today's sleep → activities → upcoming sleep.
                User sees complete picture: "I slept 01:00-07:00, now my day,
                and tonight I'll sleep again 01:00-07:00."
            """
            start_time = item.get("start_time", "00:00")
            start_min = _time_to_minutes(start_time)
            item_type = item.get("type")
            name = item.get("name", "").lower()
            event_id = item.get("event_id", "").lower()
            end_time_next_day = item.get("end_time_next_day", False)
            
            if item_type == "sleep":
                if end_time_next_day:
                    return 99999
                else:
                    return 0
            
            if (item_type == "fixed_event" and "evening" in event_id and "routine" in event_id):
                return 99998
            
            if ("evening" in name and "routine" in name):
                return 99998
            
            if start_min < 120 and "free" in name:
                return 99997
            
            return start_min
        
        kept_items.sort(key=sort_key_late_bedtime)
        
        logger.info(f"✅ Created 1 sleep block for late bedtime ({bedtime.strftime('%H:%M')}-{wake_time.strftime('%H:%M')}) + sorted {len(kept_items)} items")
        return kept_items
    
    has_morning_routine = any(
        (item.get("type") == "routine" or 
         (item.get("type") == "fixed_event" and (
             "routine" in item.get("event_id", "").lower() or
             "routine" in item.get("name", "").lower()
         ))) 
        and ("morning" in item.get("name", "").lower() or "morning" in item.get("event_id", "").lower())
        for item in schedule_items
    )
    has_evening_routine = any(
        (item.get("type") == "routine" or 
         (item.get("type") == "fixed_event" and (
             "routine" in item.get("event_id", "").lower() or
             "routine" in item.get("name", "").lower()
         ))) 
        and ("evening" in item.get("name", "").lower() or "evening" in item.get("event_id", "").lower())
        for item in schedule_items
    )
    
    bedtime = sleep_recommendation.ideal_bedtime
    wake_time = sleep_recommendation.ideal_wake_time
    
    morning_duration = 30
    evening_duration = 45
    if routine_preferences:
        morning_duration = routine_preferences.get("morning_duration_minutes", 30)
        evening_duration = routine_preferences.get("evening_duration_minutes", 45)
    
    wake_minutes = _time_to_minutes(wake_time.strftime("%H:%M"))
    morning_end_minutes = wake_minutes + morning_duration
    morning_end_time = _minutes_to_time(morning_end_minutes)
    
    bedtime_minutes = _time_to_minutes(bedtime.strftime("%H:%M"))
    evening_start_minutes = bedtime_minutes - evening_duration
    
    if evening_start_minutes < 0:
        evening_start_minutes += 1440
        logger.warning(f"⚠️ Evening routine crosses midnight backwards, adjusted to {evening_start_minutes}min")
    
    evening_start_time = _minutes_to_time(evening_start_minutes)
    
    sleep_block = {
        "type": "sleep",
        "name": "Sleep",
        "start_time": bedtime.strftime("%H:%M"),
        "end_time": wake_time.strftime("%H:%M"),
        "end_time_next_day": True,
        "description": f"Sleep from {bedtime.strftime('%H:%M')} to {wake_time.strftime('%H:%M')} (next day)"
    }
    
    morning_routine = {
        "type": "routine",
        "name": "Morning Routine",
        "start_time": wake_time.strftime("%H:%M"),
        "end_time": morning_end_time,
        "description": f"{morning_duration}-minute morning routine after waking"
    }
    
    evening_routine = {
        "type": "routine",
        "name": "Evening Routine",
        "start_time": evening_start_time,
        "end_time": bedtime.strftime("%H:%M"),
        "description": f"{evening_duration}-minute evening routine before sleep"
    }
    
    result = []
    
    if not has_morning_routine:
        result.append(morning_routine)
    
    for item in kept_items:
        result.append(item)
    
    if not has_evening_routine and evening_start_minutes < bedtime_minutes:
        result.append(evening_routine)
    elif evening_start_minutes >= bedtime_minutes:
        logger.warning(f"⚠️ Skipping evening routine - would start at/after bedtime")
    
    result.append(sleep_block)
    
    def sort_key(item):
        """
        Sorts items chronologically, with sleep block at the end (crosses midnight).
        """
        if item.get("end_time_next_day") and item.get("type") == "sleep":
            return 9999
        return _time_to_minutes(item.get("start_time", "00:00"))
    
    result.sort(key=sort_key)
    
    routines_added = (0 if has_morning_routine else 1) + (0 if has_evening_routine else 1)
    logger.info(f"✅ Sleep/Routines: {removed_count} items removed, 1 sleep block + {routines_added} routines added")
    
    return result


def _time_to_minutes(time_str: str) -> int:
    """
    Converts HH:MM time string to minutes since midnight.
    
    Used for sorting schedule items chronologically.
    """
    try:
        parts = time_str.split(":")
        h = int(parts[0])
        m = int(parts[1])
        return h * 60 + m
    except (ValueError, AttributeError, IndexError):
        return 0


def _minutes_to_time(minutes: int) -> str:
    """
    Converts minutes since midnight to HH:MM time string.
    
    Handles values >= 1440 by wrapping to next day.
    """
    minutes = minutes % 1440
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def _create_two_separate_sleep_blocks(
    schedule_items: List[Dict[str, Any]],
    sleep_blocks: List[Dict[str, Any]],
    routine_preferences: Optional[Dict[str, Any]],
    bedtime: Any,
    wake_time: Any
) -> List[Dict[str, Any]]:
    """
    Creates TWO FULL 9-HOUR sleep entries crossing midnight boundaries.
    
    Educational Note:
        Creates TWO complete sleep cycles showing full duration:
        1. Previous night: bedtime (yesterday) → wake (today) = FULL 9h
        2. Upcoming night: bedtime (today) → wake (tomorrow) = FULL 9h
        
        Example for 9h sleep (22:00→07:00):
        - Sleep #1: 22:00 (yesterday) → 07:00 (today) [displays at START]
        - Sleep #2: 22:00 (today) → 07:00 (tomorrow) [displays at END]
        
        This shows complete 3-day sleep pattern: previous → today → upcoming
    """
    bed_str = bedtime.strftime("%H:%M")
    wake_str = wake_time.strftime("%H:%M")
    bed_minutes = _time_to_minutes(bed_str)
    wake_minutes = _time_to_minutes(wake_str)
    is_late_bedtime = bed_minutes < wake_minutes
    
    logger.info(f"🔍 Processing sleep blocks: bed={bed_str} ({bed_minutes}min), wake={wake_str} ({wake_minutes}min), late_bedtime={is_late_bedtime}")
    logger.info(f"🔍 Sleep blocks received: {len(sleep_blocks)}")
    for idx, block in enumerate(sleep_blocks):
        logger.info(f"   Block {idx+1}: start={block.get('start_time')}, end={block.get('end_time')}, event_id={block.get('event_id')}")
    
    morning_sleep = {
        "type": "sleep",
        "name": "Sleep",
        "start_time": bed_str,
        "end_time": wake_str,
        "end_time_next_day": False,
        "description": f"Sleep from {bed_str} (yesterday) to {wake_str} (today) - FULL previous night cycle"
    }
    
    evening_sleep = {
        "type": "sleep",
        "name": "Sleep",
        "start_time": bed_str,
        "end_time": wake_str,
        "end_time_next_day": True,
        "description": f"Sleep from {bed_str} (today) to {wake_str} (tomorrow) - FULL upcoming night cycle"
    }
    
    other_items = [
        item for item in schedule_items
        if item not in sleep_blocks
    ]
    
    if is_late_bedtime:
        filtered_items = []
        for item in other_items:
            if item.get("type") == "free_time":
                item_start = _time_to_minutes(item.get("start_time", "00:00"))
                item_end = _time_to_minutes(item.get("end_time", "00:00"))
                
                overlaps_first_sleep = (
                    (item_start >= bed_minutes and item_start < wake_minutes) or
                    (item_end > bed_minutes and item_end <= wake_minutes) or
                    (item_start <= bed_minutes and item_end >= wake_minutes)
                )
                
                if overlaps_first_sleep:
                    logger.info(f"   🗑️ Removing Free Time {item.get('start_time')}-{item.get('end_time')} (overlaps with first sleep {bed_str}-{wake_str})")
                    continue
            
            filtered_items.append(item)
        
        other_items = filtered_items
    
    for item in other_items:
        if item.get("type") == "free_time" and "evening" in item.get("name", "").lower():
            item["name"] = "Free Time"
            logger.info(f"   🔧 Normalized Free Time name: '{item.get('name')}' → 'Free Time'")
    
    if is_late_bedtime:
        has_evening_routine = any(
            item.get("type") == "fixed_event" and 
            (item.get("event_id") == "evening_routine" or
             ("evening" in item.get("name", "").lower() and "routine" in item.get("name", "").lower()))
            for item in other_items
        )
        
        if not has_evening_routine:
            evening_duration = routine_preferences.get("evening_duration_minutes", 45) if routine_preferences else 45
            evening_start_min = bed_minutes - evening_duration
            if evening_start_min < 0:
                evening_start_min += 1440
            
            evening_routine = {
                "type": "fixed_event",
                "event_id": "evening_routine",
                "name": "Evening Routine",
                "start_time": _minutes_to_time(evening_start_min),
                "end_time": bed_str,
                "duration_minutes": evening_duration,
            }
            other_items.append(evening_routine)
            logger.info(f"   ⚠️ Evening Routine missing from LLM, re-adding: {_minutes_to_time(evening_start_min)}-{bed_str}")
            
            for item in other_items:
                if item.get("type") == "free_time":
                    old_end = item.get("end_time")
                    item["end_time"] = _minutes_to_time(evening_start_min)
                    logger.info(f"   🔧 Fixed Free Time end_time: {old_end} → {_minutes_to_time(evening_start_min)}")
    
    other_items.append(morning_sleep)
    other_items.append(evening_sleep)
    
    bed_minutes = _time_to_minutes(bed_str)
    wake_minutes = _time_to_minutes(wake_str)
    
    def sort_key_full_sleep(item):
        """
        Sorts schedule items to show proper daily flow:
        1. First sleep (previous night) - priority 0
        2. Morning routine and day activities - priority 1 (by start time)
        3. Evening routine (if late bedtime) - priority 98999 (just before second sleep)
        4. Second sleep (upcoming night) - priority 99999
        
        Educational Note:
            For late bedtime (01:00), evening routine (00:15-01:00) must appear
            BEFORE second sleep, not after first sleep. We give it priority 98999
            so it sorts between day activities (priority 1) and second sleep (99999).
            
            CRITICAL: Check both event_id (solver) AND name (LLM) for evening routine!
        """
        item_type = item.get("type")
        end_next_day = item.get("end_time_next_day", False)
        event_id = item.get("event_id", "")
        name = item.get("name", "").lower()
        
        if item_type == "sleep" and not end_next_day:
            return (0, 0)
        
        is_evening_routine = (
            (item_type == "fixed_event" and event_id == "evening_routine") or
            (item_type == "fixed_event" and "evening" in name and "routine" in name)
        )
        if is_evening_routine:
            return (98999, 0)
        
        start_min = _time_to_minutes(item.get("start_time", "00:00"))
        return (1, start_min) if not end_next_day else (99999, 0)
    
    other_items.sort(key=sort_key_full_sleep)
    
    logger.info(f"✅ Created 2 FULL sleep cycles: previous night {bed_str}(yesterday)→{wake_str}(today) + upcoming night {bed_str}(today)→{wake_str}(tomorrow)")
    return other_items


def _create_two_sleep_from_single_block(
    schedule_items: List[Dict[str, Any]],
    previous_block: Dict[str, Any],
    routine_preferences: Optional[Dict[str, Any]],
    bedtime: Any,
    wake_time: Any
) -> List[Dict[str, Any]]:
    """
    Creates TWO FULL sleep cycles even when only single solver block exists.
    
    Educational Note:
        Even with only previous_night block from solver, we create
        TWO COMPLETE 9-hour sleep cycles for full daily schedule:
        
        1. Previous night: bedtime (yesterday) → wake (today) = FULL 9h
        2. Upcoming night: bedtime (today) → wake (tomorrow) = FULL 9h
        
        Example for 9h sleep (22:00→07:00):
        - Sleep #1: 22:00 (yesterday) → 07:00 (today) [displays at START]
        - Sleep #2: 22:00 (today) → 07:00 (tomorrow) [displays at END]
        
        This ensures consistent 3-day visualization: previous → today → upcoming
    """
    bed_str = bedtime.strftime("%H:%M")
    wake_str = wake_time.strftime("%H:%M")
    
    bed_minutes = _time_to_minutes(bed_str)
    wake_minutes = _time_to_minutes(wake_str)
    is_late_bedtime = bed_minutes < wake_minutes
    
    other_items = [
        item for item in schedule_items
        if item != previous_block
    ]
    
    if is_late_bedtime:
        logger.info(f"🌙 DETERMINISTIC LATE BEDTIME: bed={bed_str} < wake={wake_str}")
        
        has_evening_routine = any(
            item.get("type") == "fixed_event" and 
            (("evening" in item.get("event_id", "").lower() and "routine" in item.get("event_id", "").lower()) or
             ("evening" in item.get("name", "").lower() and "routine" in item.get("name", "").lower()))
            for item in other_items
        )
        
        if not has_evening_routine:
            logger.info(f"   ⚠️ Evening Routine missing in deterministic, adding it")
            evening_duration = routine_preferences.get("evening_duration_minutes", 45) if routine_preferences else 45
            evening_start_min = bed_minutes - evening_duration
            if evening_start_min < 0:
                evening_start_min += 1440
            
            evening_routine = {
                "type": "fixed_event",
                "event_id": "evening_routine",
                "name": "Evening Routine",
                "start_time": _minutes_to_time(evening_start_min),
                "end_time": bed_str,
                "duration_minutes": evening_duration,
            }
            other_items.append(evening_routine)
            evening_routine_start = _minutes_to_time(evening_start_min)
        else:
            evening_item = next((item for item in other_items if item.get("type") == "fixed_event" and "evening" in item.get("name", "").lower() and "routine" in item.get("name", "").lower()), None)
            evening_routine_start = evening_item.get("start_time") if evening_item else "00:15"
        
        for item in other_items:
            if item.get("type") == "free_time":
                old_end = item.get("end_time")
                item["end_time"] = evening_routine_start
                logger.info(f"   🔧 Fixed Free Time end_time: {old_end} → {evening_routine_start}")
        
        main_sleep_block = {
            "type": "sleep",
            "name": "Sleep",
            "start_time": bed_str,
            "end_time": wake_str,
            "end_time_next_day": False,
            "description": f"Sleep from {bed_str} (yesterday/today) to {wake_str} (today) - FULL current night cycle"
        }
        
        other_items.append(main_sleep_block)
        
        upcoming_sleep_block = {
            "type": "sleep",
            "name": "Sleep",
            "start_time": bed_str,
            "end_time": wake_str,
            "end_time_next_day": True,
            "description": f"Sleep from {bed_str} (today) to {wake_str} (tomorrow) - FULL upcoming night cycle"
        }
        
        other_items.append(upcoming_sleep_block)
        logger.info(f"   ✅ Added 2 FULL sleep cycles (deterministic): {bed_str}(yesterday)→{wake_str}(today) + {bed_str}(today)→{wake_str}(tomorrow)")
    else:
        morning_sleep = {
            "type": "sleep",
            "name": "Sleep",
            "start_time": bed_str,
            "end_time": wake_str,
            "end_time_next_day": False,
            "description": f"Sleep from {bed_str} (yesterday) to {wake_str} (today) - FULL previous night cycle"
        }
        
        evening_sleep = {
            "type": "sleep",
            "name": "Sleep",
            "start_time": bed_str,
            "end_time": wake_str,
            "end_time_next_day": True,
            "description": f"Sleep from {bed_str} (today) to {wake_str} (tomorrow) - FULL upcoming night cycle"
        }
        
        other_items.append(morning_sleep)
        other_items.append(evening_sleep)
        logger.info(f"   ✅ Added 2 FULL sleep cycles (deterministic normal): {bed_str}(yesterday)→{wake_str}(today) + {bed_str}(today)→{wake_str}(tomorrow)")
    
    def sort_key_late_bedtime(item):
        """
        Sorts for late bedtime with realistic daily structure.
        
        Order:
        1. Sleep current night (01:00-07:00) - priority 0 (FIRST)
        2. Morning routine (07:00-07:30) - priority by start_time
        3. Regular schedule (07:30-20:20) - priority by start_time
        4. Free Time crossing midnight (20:20-00:15) - priority 99997
        5. Evening routine (00:15-01:00) - priority 99998
        6. Sleep next night (01:00-07:00 next day) - priority 99999 (LAST)
        """
        start_time = item.get("start_time", "00:00")
        start_min = _time_to_minutes(start_time)
        item_type = item.get("type")
        name = item.get("name", "").lower()
        event_id = item.get("event_id", "").lower()
        end_time_next_day = item.get("end_time_next_day", False)
        
        if is_late_bedtime:
            if item_type == "sleep":
                if end_time_next_day:
                    return 99999
                else:
                    return 0
            
            if (item_type == "fixed_event" and "evening" in event_id and "routine" in event_id):
                return 99998
            
            if ("evening" in name and "routine" in name):
                return 99998
            
            if start_min < 120 and "free" in name:
                return 99997
        
        return start_min
    
    other_items.sort(key=sort_key_late_bedtime)
    
    logger.info(f"✅ Created 2 FULL sleep cycles from single block: {bed_str}(yesterday)→{wake_str}(today) + {bed_str}(today)→{wake_str}(tomorrow)")
    return other_items


def _merge_two_sleep_blocks_and_return_schedule(
    schedule_items: List[Dict[str, Any]],
    sleep_blocks: List[Dict[str, Any]],
    routine_preferences: Optional[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    [DEPRECATED] Old merging logic - kept for compatibility.
    
    Educational Note:
        This function is no longer used as we now show TWO separate
        sleep entries instead of merging them into one.
    """
    previous = next((b for b in sleep_blocks if b.get("event_id") == "sleep_previous_night"), None)
    upcoming = next((b for b in sleep_blocks if b.get("event_id") == "sleep_upcoming_night"), None)
    
    if not previous or not upcoming:
        logger.warning("⚠️ Missing previous or upcoming sleep block, returning original schedule")
        return schedule_items
    
    wake_time = previous.get("end_time")
    bedtime = upcoming.get("start_time")
    
    wake_minutes = _time_to_minutes(wake_time)
    bed_minutes = _time_to_minutes(bedtime)
    
    if bed_minutes < wake_minutes:
        display_bedtime = bedtime
        logger.info(f"🛏️ Late bedtime detected: {bedtime} (after midnight) → {wake_time}")
    else:
        display_bedtime = bedtime
        logger.info(f"🛏️ Normal sleep: {bedtime} → {wake_time} (next day)")
    
    merged_sleep = {
        "type": "sleep",
        "name": "Sleep",
        "start_time": display_bedtime,
        "end_time": wake_time,
        "end_time_next_day": True,
        "description": f"Sleep from {display_bedtime} to {wake_time} (next day)"
    }
    
    other_items = [
        item for item in schedule_items
        if item not in sleep_blocks
    ]
    
    other_items.append(merged_sleep)
    
    other_items.sort(key=lambda x: (
        9999 if x.get("end_time_next_day") else _time_to_minutes(x.get("start_time", "00:00"))
    ))
    
    logger.info(f"✅ Merged 2 sleep blocks into 1 continuous display: {display_bedtime} → {wake_time}")
    return other_items
