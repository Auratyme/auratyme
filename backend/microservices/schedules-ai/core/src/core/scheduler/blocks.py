"""
Schedule block collection and assembly.

This module handles collecting all schedule components (tasks, events,
meals, routines, activities) into unified block format for processing.
"""

import logging
from datetime import time
from typing import Any, Dict, List, Tuple, TYPE_CHECKING

from src.utils.time_utils import time_to_total_minutes, total_minutes_to_time
from src.core.scheduler.sleep_merger import merge_sleep_blocks

if TYPE_CHECKING:
    from src.core.solver import ScheduledTaskInfo
    from src.core.scheduler.models import ScheduleInputData
    from src.core.sleep import SleepMetrics

logger = logging.getLogger(__name__)


def collect_all_schedule_blocks(
    core_schedule: List["ScheduledTaskInfo"],
    input_data: "ScheduleInputData",
    sleep_metrics: "SleepMetrics",
    prepare_solver_input_func,
    prepare_profile_func
) -> List[Tuple[int, int, Dict[str, Any]]]:
    """
    Collects all schedule blocks: fixed events, tasks, activities.
    
    Educational Note:
        Tuple format (start_minutes, end_minutes, metadata) enables
        efficient sorting and conflict detection.
        
        Sleep blocks are merged after collection to present a single
        continuous sleep period to users instead of separate technical blocks.
        
        CRITICAL: Routines AND LUNCH are added as fixed_events in solver_prep
        BEFORE solver runs, ensuring they get priority placement. This function
        only collects blocks AFTER solver schedules tasks around fixed events.
    """
    blocks = []
    
    add_fixed_event_blocks(
        blocks, input_data, sleep_metrics,
        prepare_solver_input_func, prepare_profile_func
    )
    
    add_task_blocks(blocks, core_schedule, input_data)
    add_activity_blocks(blocks, input_data, sleep_metrics)
    
    blocks = merge_sleep_blocks(blocks, sleep_metrics)
    blocks.sort(key=lambda x: x[0])
    return blocks


def add_fixed_event_blocks(
    blocks, input_data, sleep_metrics,
    prepare_solver_input_func, prepare_profile_func
) -> None:
    """
    Adds fixed events (meetings, appointments, sleep) to blocks.
    
    Educational Note:
        Fixed events have highest priority and cannot be moved.
        Sleep included as fixed event to reserve time.
        Sleep metadata includes ideal bed/wake times for display.
    """
    profile = prepare_profile_func(input_data)
    solver_result = prepare_solver_input_func(
        input_data, profile, sleep_metrics
    )
    
    if not solver_result:
        return
    
    solver_input, _, _ = solver_result
    
    bed_min = time_to_total_minutes(sleep_metrics.ideal_bedtime) if sleep_metrics else 23 * 60 + 30
    wake_min = time_to_total_minutes(sleep_metrics.ideal_wake_time) if sleep_metrics else 7 * 60
    
    for fixed_event in solver_input.fixed_events:
        event_name = _format_event_name(fixed_event)
        
        meta = {
            "type": "fixed_event",
            "event_id": fixed_event.id,
            "name": event_name,
            "start_time": total_minutes_to_time(fixed_event.start_minutes).strftime("%H:%M"),
            "end_time": total_minutes_to_time(fixed_event.end_minutes).strftime("%H:%M"),
            "duration_minutes": fixed_event.end_minutes - fixed_event.start_minutes,
        }
        
        if fixed_event.id in ["sleep_previous_night", "sleep_upcoming_night"]:
            meta["ideal_bedtime_minutes"] = bed_min
            meta["ideal_wake_minutes"] = wake_min
        
        blocks.append((
            fixed_event.start_minutes,
            fixed_event.end_minutes,
            meta
        ))


def _format_event_name(fixed_event) -> str:
    """
    Formats event name for display.
    
    Educational Note:
        Fallback to ID when name unavailable, with title case
        and underscore replacement for readability.
    """
    if fixed_event.name:
        return fixed_event.name
    
    return fixed_event.id.replace("_", " ").title()


def add_task_blocks(
    blocks, core_schedule, input_data
) -> None:
    """
    Adds scheduled tasks to blocks.
    
    Educational Note:
        Matches task IDs to find original task titles.
        Time conversion ensures consistent format across schedule.
    """
    for task_info in core_schedule:
        task_name = _find_task_name(task_info.task_id, input_data.tasks)
        
        start_min = time_to_total_minutes(task_info.start_time)
        end_min = time_to_total_minutes(task_info.end_time)
        
        blocks.append((
            start_min,
            end_min,
            {
                "type": "task",
                "task_id": str(task_info.task_id),
                "name": task_name,
                "start_time": task_info.start_time.strftime("%H:%M"),
                "end_time": task_info.end_time.strftime("%H:%M"),
                "duration_minutes": end_min - start_min,
            }
        ))


def _find_task_name(task_id, tasks) -> str:
    """
    Finds task title by ID.
    
    Educational Note:
        Fallback to generic "Task" when ID not found,
        ensuring schedule generation continues despite missing data.
    """
    for task in tasks:
        if str(task.id) == str(task_id):
            return task.title
    
    return "Task"


def add_routine_blocks(
    blocks, sleep_metrics, input_data
) -> None:
    """
    Adds morning and evening routines to blocks.
    
    Educational Note:
        Routines anchored to sleep times (after wake, before bed)
        to establish consistent daily rhythm.
    """
    prefs = input_data.preferences or {}
    routine_prefs = prefs.get("routines", {})
    
    morning_duration = routine_prefs.get("morning_duration_minutes", 30)
    evening_duration = routine_prefs.get("evening_duration_minutes", 45)
    
    wake_min = time_to_total_minutes(sleep_metrics.ideal_wake_time)
    bed_min = time_to_total_minutes(sleep_metrics.ideal_bedtime)
    
    _add_morning_routine_block(blocks, wake_min, morning_duration)
    _add_evening_routine_block(blocks, bed_min, evening_duration)


def _add_morning_routine_block(
    blocks, wake_time_minutes, duration
) -> None:
    """
    Adds morning routine immediately after wake time.
    
    Educational Note:
        Morning routine sets tone for day. Starting right after
        wake ensures it happens before other commitments.
    """
    start = wake_time_minutes
    end = start + duration
    
    blocks.append((
        start,
        end,
        {
            "type": "routine",
            "name": "Morning Routine",
            "start_time": total_minutes_to_time(start).strftime("%H:%M"),
            "end_time": total_minutes_to_time(end).strftime("%H:%M"),
            "duration_minutes": duration,
        }
    ))


def _add_evening_routine_block(
    blocks, bedtime_minutes, duration
) -> None:
    """
    Adds evening routine before bedtime.
    
    Educational Note:
        Evening routine aids wind-down for better sleep quality.
        Positioned to end exactly at bedtime.
    """
    end = bedtime_minutes
    start = max(0, end - duration)
    
    blocks.append((
        start,
        end,
        {
            "type": "routine",
            "name": "Evening Routine",
            "start_time": total_minutes_to_time(start).strftime("%H:%M"),
            "end_time": total_minutes_to_time(end).strftime("%H:%M"),
            "duration_minutes": duration,
        }
    ))


def add_meal_blocks(blocks, input_data, wake_time: int) -> None:
    """
    Adds ONLY lunch meal with intelligent 3-tier placement.
    
    PRIORITY 1: Ideal window 12:00-15:00 (adjusted by wake time)
    PRIORITY 2: Immediately after work (if ideal blocked)
    PRIORITY 3: Best available gap (closest to noon)
    
    Educational Note:
        Breakfast is part of morning routine after waking.
        Dinner is part of evening routine before sleep.
        Lunch has HIGHER PRIORITY than regular tasks and uses
        intelligent placement to ensure biological optimal timing
        while respecting fixed commitments. Always added.
    """
    prefs = input_data.preferences or {}
    meal_prefs = prefs.get("meals", {})
    
    existing_meals = _find_existing_meal_types(blocks)
    
    if not existing_meals.get("lunch"):
        lunch_duration = meal_prefs.get("lunch_duration_minutes", 30)
        lunch_start_min = _find_lunch_start_time(blocks, lunch_duration, wake_time)
        _add_meal_block(blocks, "Lunch", (lunch_start_min, lunch_duration))


def _find_existing_meal_types(
    blocks
) -> Dict[str, bool]:
    """
    Identifies which meals already exist as fixed events.
    
    Educational Note:
        Case-insensitive check handles various naming conventions
        for meal events (breakfast, Breakfast, BREAKFAST, etc.).
    """
    existing = {"breakfast": False, "lunch": False, "dinner": False}
    
    for _, _, meta in blocks:
        if meta.get("type") == "fixed_event":
            event_name_lower = meta["name"].lower()
            
            if "breakfast" in event_name_lower:
                existing["breakfast"] = True
            elif "lunch" in event_name_lower:
                existing["lunch"] = True
            elif "dinner" in event_name_lower:
                existing["dinner"] = True
    
    return existing


def _add_meal_block(
    blocks,
    meal_name: str,
    meal_timing: Tuple[int, int]
) -> None:
    """
    Adds a single meal block to schedule.
    
    Educational Note:
        Consistent meal times support healthy eating patterns
        and energy management throughout day.
    """
    start_min, duration = meal_timing
    end_min = start_min + duration
    
    blocks.append((
        start_min,
        end_min,
        {
            "type": "meal",
            "name": meal_name,
            "start_time": total_minutes_to_time(start_min).strftime("%H:%M"),
            "end_time": total_minutes_to_time(end_min).strftime("%H:%M"),
            "duration_minutes": duration,
        }
    ))


def add_activity_blocks(
    blocks, input_data, sleep_metrics
) -> None:
    """
    Adds physical activities based on user goals and frequency.
    
    Educational Note:
        Activity scheduling respects frequency preferences (daily,
        specific days) and preferred times (morning, evening, etc.).
    """
    prefs = input_data.preferences or {}
    activity_goals = prefs.get("activity_goals", [])
    
    wake_min = time_to_total_minutes(sleep_metrics.ideal_wake_time)
    bed_min = time_to_total_minutes(sleep_metrics.ideal_bedtime)
    
    routines = prefs.get("routines", {})
    morning_routine_dur = routines.get("morning_duration_minutes", 30)
    evening_routine_dur = routines.get("evening_duration_minutes", 45)
    
    weekday = input_data.target_date.strftime("%a").lower()
    
    for activity in activity_goals:
        if _should_schedule_activity(activity, weekday):
            _add_single_activity_block(
                blocks, activity, wake_min, bed_min,
                morning_routine_dur, evening_routine_dur
            )


def _should_schedule_activity(
    activity: dict,
    weekday: str
) -> bool:
    """
    Determines if activity should be scheduled on this day.
    
    Educational Note:
        Supports multiple frequency formats: "daily", comma-separated
        days, or day prefix matching for flexible activity planning.
    """
    frequency = activity.get("frequency", "daily").lower()
    
    if frequency == "daily":
        return True
    
    if weekday in frequency.split(","):
        return True
    
    if frequency.startswith(weekday[:3]):
        return True
    
    return False


def _add_single_activity_block(
    blocks, activity, wake_min, bed_min,
    morning_routine_dur, evening_routine_dur
) -> None:
    """
    Adds a single activity block at preferred time.
    
    Educational Note:
        Time preference (morning, evening, afternoon, before_sleep)
        determines activity placement for optimal user experience.
    """
    name = activity.get("name", "Activity")
    duration = activity.get("duration_minutes", 60)
    preferred_times = activity.get("preferred_time", ["evening"])
    
    start = _calculate_activity_start_time(
        preferred_times, wake_min, bed_min,
        morning_routine_dur, evening_routine_dur, duration
    )
    
    blocks.append((
        start,
        start + duration,
        {
            "type": "activity",
            "name": name,
            "start_time": total_minutes_to_time(start).strftime("%H:%M"),
            "end_time": total_minutes_to_time(start + duration).strftime("%H:%M"),
            "duration_minutes": duration,
        }
    ))


def _calculate_activity_start_time(
    preferred_times, wake_min, bed_min,
    morning_routine_dur, evening_routine_dur, activity_duration
) -> int:
    """
    Calculates activity start time based on preference.
    
    Educational Note:
        Different preferred times map to different day segments:
        morning after routine, evening at 18:00, afternoon at 15:00,
        before_sleep leaves buffer before bedtime routine.
    """
    if "morning" in preferred_times:
        return wake_min + morning_routine_dur + 30
    
    if "before_sleep" in preferred_times:
        return bed_min - evening_routine_dur - activity_duration - 30
    
    if "afternoon" in preferred_times:
        return 900
    
    return 1080


def _find_lunch_start_time(blocks, lunch_duration: int, wake_time: int) -> int:
    """
    Finds optimal lunch time using 3-tier priority cascade.
    
    PRIORITY 1 (12:00-15:00): Biological optimal window
    PRIORITY 2 (post-work): Immediately after work ends  
    PRIORITY 3 (fallback): Best available gap anywhere
    
    Educational Note:
        Lunch has higher priority than regular tasks. System tries
        to place lunch in ideal biological window (12:00-15:00),
        adjusts for wake time, and falls back to post-work if needed.
        Lunch is ALWAYS added (never skipped) - it's essential meal.
    """
    logger = logging.getLogger(__name__)
    ideal_start, ideal_end = _calculate_ideal_lunch_window(wake_time)
    
    logger.info(f"🍽️ Finding lunch placement (duration: {lunch_duration}min)")
    logger.info(f"   Wake time: {wake_time}min → Ideal window: {ideal_start}-{ideal_end}min")
    
    lunch_slot = _find_gap_in_window(blocks, ideal_start, ideal_end, lunch_duration)
    if lunch_slot is not None:
        logger.info(f"✅ PRIORITY 1: Lunch placed in ideal window → {lunch_slot}min ({total_minutes_to_time(lunch_slot).strftime('%H:%M')})")
        return lunch_slot
    
    logger.info("⚠️ PRIORITY 1 failed: No gap in ideal window, trying PRIORITY 2...")
    work_end = _find_work_end_time(blocks)
    if work_end:
        logger.info(f"   Work ends at {work_end}min ({total_minutes_to_time(work_end).strftime('%H:%M')})")
        post_work_slot = _try_post_work_lunch(blocks, work_end, lunch_duration)
        if post_work_slot is not None:
            logger.info(f"✅ PRIORITY 2: Lunch placed after work → {post_work_slot}min ({total_minutes_to_time(post_work_slot).strftime('%H:%M')})")
            return post_work_slot
    
    logger.info("⚠️ PRIORITY 2 failed: Using PRIORITY 3 (best available gap)...")
    best_gap = _find_best_available_gap(blocks, lunch_duration)
    logger.info(f"✅ PRIORITY 3: Lunch placed in best gap → {best_gap}min ({total_minutes_to_time(best_gap).strftime('%H:%M')})")
    return best_gap


def _calculate_ideal_lunch_window(wake_time: int) -> tuple:
    """
    Calculates ideal lunch window based on wake time.
    
    Educational Note:
        Adjusts lunch window based on chronotype habits:
        Early wake → earlier lunch, Late wake → later lunch.
    """
    if wake_time < 7 * 60:
        return (11 * 60 + 30, 14 * 60 + 30)
    elif wake_time > 9 * 60:
        return (12 * 60 + 30, 15 * 60 + 30)
    else:
        return (12 * 60, 15 * 60)


def _find_work_end_time(blocks) -> int:
    """
    Finds work end time from blocks.
    
    Educational Note:
        Returns end time of work block or commute_from_work
        (whichever is later) for post-work lunch placement.
    """
    work_end = None
    commute_end = None
    
    for start_min, end_min, meta in blocks:
        event_id = meta.get("event_id", "")
        if event_id == "work":
            work_end = end_min
        elif event_id == "commute_from_work":
            commute_end = end_min
    
    return commute_end if commute_end else work_end


def _find_gap_in_window(blocks, window_start: int, window_end: int, duration: int):
    """
    Finds suitable gap within specified time window.
    
    Educational Note:
        Searches for first available gap that can fit lunch
        duration within the ideal biological window.
    """
    gaps = _extract_gaps_in_range(blocks, window_start, window_end)
    for gap_start, gap_end in gaps:
        if (gap_end - gap_start) >= duration:
            return gap_start
    return None


def _extract_gaps_in_range(blocks, range_start: int, range_end: int) -> list:
    """
    Extracts all available gaps within time range.
    
    Educational Note:
        Identifies free time slots between fixed blocks
        where lunch could potentially be placed.
    """
    sorted_blocks = sorted(
        [(s, e) for s, e, m in blocks if s < range_end and e > range_start],
        key=lambda x: x[0]
    )
    
    gaps = []
    current_time = range_start
    
    for block_start, block_end in sorted_blocks:
        if block_start > current_time:
            gaps.append((current_time, block_start))
        current_time = max(current_time, block_end)
    
    if current_time < range_end:
        gaps.append((current_time, range_end))
    
    return gaps


def _try_post_work_lunch(blocks, work_end: int, duration: int):
    """
    Tries to place lunch immediately after work.
    
    Educational Note:
        PRIORITY 2: If ideal window blocked, place lunch
        right after work ends (realistic user behavior).
    """
    if _is_time_slot_free(blocks, work_end, work_end + duration):
        return work_end
    return None


def _is_time_slot_free(blocks, slot_start: int, slot_end: int) -> bool:
    """
    Checks if time slot is completely free.
    
    Educational Note:
        Validates no overlap with existing fixed blocks
        to prevent scheduling conflicts.
    """
    for block_start, block_end, _ in blocks:
        if not (slot_end <= block_start or slot_start >= block_end):
            return False
    return True


def _find_best_available_gap(blocks, duration: int) -> int:
    """
    Finds best available gap anywhere in day (fallback).
    
    Educational Note:
        PRIORITY 3: Last resort - finds any suitable gap
        preferring slots closest to biological noon (12:00).
        Always returns valid time (lunch never skipped).
    """
    gaps = _extract_gaps_in_range(blocks, 6 * 60, 22 * 60)
    suitable_gaps = [(s, e) for s, e in gaps if (e - s) >= duration]
    
    if suitable_gaps:
        noon = 12 * 60
        closest_gap = min(
            suitable_gaps, 
            key=lambda g: abs((g[0] + g[1]) // 2 - noon)
        )
        return closest_gap[0]
    
    return 12 * 60
