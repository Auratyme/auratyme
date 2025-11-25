"""
LLM schedule validation and correction.

This module validates LLM-generated schedules against solver constraints
and corrects any violations by falling back to deterministic schedule generation.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def validate_llm_schedule(
    llm_schedule: Dict[str, Any],
    solver_schedule: List[Any],
    sleep_metrics: Any,
    input_data: Any
) -> Optional[Dict[str, List[str]]]:
    """
    Validates LLM schedule output against hard constraints.
    
    Educational Note:
        Multi-layer validation ensures LLM output quality.
        Returns error dict if validation fails, None if passes.
        
    Args:
        llm_schedule: Schedule dict from LLM with 'schedule' key
        solver_schedule: Original solver output with task timings
        sleep_metrics: Sleep recommendation data
        input_data: Original schedule input data
        
    Returns:
        Dict with error lists if validation fails, None if passes
    """
    errors = {
        "overlaps": [],
        "missing_sleep": [],
        "modified_tasks": [],
        "invalid_times": [],
        "ordering": []
    }
    
    schedule_items = llm_schedule.get("schedule", [])
    
    if not schedule_items:
        errors["invalid_times"].append("Empty schedule returned by LLM")
        return errors
    
    _check_for_overlaps(schedule_items, errors)
    _check_sleep_blocks(schedule_items, sleep_metrics, errors)
    _check_task_preservation(schedule_items, solver_schedule, errors)
    _check_time_validity(schedule_items, errors)
    _check_chronological_order(schedule_items, errors)
    
    has_errors = any(error_list for error_list in errors.values())
    
    if has_errors:
        logger.error("❌ LLM schedule validation FAILED:")
        for error_type, error_list in errors.items():
            if error_list:
                logger.error(f"  {error_type}: {len(error_list)} issues")
                for err in error_list[:3]:
                    logger.error(f"    - {err}")
        return errors
    
    logger.info("✅ LLM schedule validation PASSED")
    return None


def _check_for_overlaps(
    items: List[Dict[str, Any]],
    errors: Dict[str, List[str]]
) -> None:
    """
    Checks for overlapping time blocks.
    
    Educational Note:
        Overlaps are the most critical error - they make schedules
        physically impossible to execute. Items with next_day=True
        are handled specially as they cross midnight.
    """
    items_without_nextday = [
        item for item in items 
        if not item.get("next_day") and item.get("type") != "sleep"
    ]
    sorted_items = sorted(
        items_without_nextday, 
        key=lambda x: _time_to_minutes(x.get("start_time", "00:00"))
    )
    
    for i in range(len(sorted_items) - 1):
        current = sorted_items[i]
        next_item = sorted_items[i + 1]
        
        current_end = _time_to_minutes(current.get("end_time", "00:00"))
        next_start = _time_to_minutes(next_item.get("start_time", "00:00"))
        
        if current_end > next_start:
            error_msg = (
                f"Overlap: '{current.get('name')}' "
                f"({current.get('start_time')}-{current.get('end_time')}) "
                f"overlaps with '{next_item.get('name')}' "
                f"({next_item.get('start_time')}-{next_item.get('end_time')})"
            )
            errors["overlaps"].append(error_msg)


def _check_sleep_blocks(
    items: List[Dict[str, Any]],
    sleep_metrics: Any,
    errors: Dict[str, List[str]]
) -> None:
    """
    Verifies sleep blocks exist (1 or 2 depending on bedtime).
    
    Educational Note:
        Daily schedule needs 1-2 sleep blocks:
        - Late bedtime (after midnight): 1 block (01:00-07:00 same day)
        - Normal bedtime (before midnight): 2 blocks (23:00-07:00 crossing midnight)
    """
    if not sleep_metrics:
        return
    
    sleep_blocks = [item for item in items if item.get("type") == "sleep"]
    wake_time = sleep_metrics.ideal_wake_time.strftime("%H:%M")
    bed_time = sleep_metrics.ideal_bedtime.strftime("%H:%M")
    
    bed_minutes = _time_to_minutes(bed_time)
    wake_minutes = _time_to_minutes(wake_time)
    is_late_bedtime = bed_minutes < wake_minutes
    
    expected_blocks = 1 if is_late_bedtime else 2
    
    if len(sleep_blocks) < expected_blocks:
        errors["missing_sleep"].append(
            f"Expected {expected_blocks} sleep block(s) ({bed_time}-{wake_time}), found {len(sleep_blocks)}"
        )
        return
    
    sleep_blocks_correct = sum(
        1 for item in sleep_blocks
        if (item.get("start_time") == bed_time or item.get("start_time") == "00:00") and
           (item.get("end_time") == wake_time or item.get("end_time") == "23:59")
    )
    
    if sleep_blocks_correct < expected_blocks:
        errors["missing_sleep"].append(
            f"Expected {expected_blocks} sleep block(s) ({bed_time}-{wake_time}), found {sleep_blocks_correct} matching"
        )


def _check_task_preservation(
    items: List[Dict[str, Any]],
    solver_schedule: List[Any],
    errors: Dict[str, List[str]]
) -> None:
    """
    Verifies all solver tasks appear with exact original times.
    
    Educational Note:
        Solver tasks represent hard constraints that LLM must not modify.
        Any deviation indicates LLM ignored critical instructions.
    """
    task_items = [item for item in items if item.get("type") == "task"]
    
    if len(task_items) < len(solver_schedule):
        errors["modified_tasks"].append(
            f"Missing tasks: expected {len(solver_schedule)}, got {len(task_items)}"
        )
    
    for solver_task in solver_schedule:
        expected_start = solver_task.start_time.strftime("%H:%M")
        expected_end = solver_task.end_time.strftime("%H:%M")
        task_id = str(solver_task.task_id)
        
        matching_task = next(
            (item for item in task_items if item.get("task_id") == task_id),
            None
        )
        
        if not matching_task:
            errors["modified_tasks"].append(
                f"Task {task_id} missing from LLM schedule"
            )
            continue
        
        actual_start = matching_task.get("start_time")
        actual_end = matching_task.get("end_time")
        
        if actual_start != expected_start or actual_end != expected_end:
            errors["modified_tasks"].append(
                f"Task {task_id} times changed: "
                f"expected {expected_start}-{expected_end}, "
                f"got {actual_start}-{actual_end}"
            )


def _check_time_validity(
    items: List[Dict[str, Any]],
    errors: Dict[str, List[str]]
) -> None:
    """
    Validates time format and logical consistency.
    
    Educational Note:
        Basic sanity checks prevent impossible schedules.
        Items can cross midnight (e.g., Free Time 20:00-00:15)
        which is valid when end_time < start_time in minutes.
    """
    for item in items:
        start_time = item.get("start_time")
        end_time = item.get("end_time")
        name = item.get("name", "Unknown")
        item_type = item.get("type")
        
        if not start_time or not end_time:
            errors["invalid_times"].append(
                f"Item '{name}' missing start_time or end_time"
            )
            continue
        
        try:
            start_min = _time_to_minutes(start_time)
            end_min = _time_to_minutes(end_time)
            
            if end_time in ["23:59", "24:00"]:
                continue
            
            if item_type in ["free_time", "sleep"]:
                continue
            
            if start_min >= end_min:
                errors["invalid_times"].append(
                    f"Item '{name}' has end_time ({end_time}) "
                    f"<= start_time ({start_time})"
                )
        except ValueError:
            errors["invalid_times"].append(
                f"Item '{name}' has invalid time format "
                f"(start: {start_time}, end: {end_time})"
            )


def _check_chronological_order(
    items: List[Dict[str, Any]],
    errors: Dict[str, List[str]]
) -> None:
    """
    Verifies items are in chronological order.
    
    Educational Note:
        Chronological order is required for proper schedule display.
        Items with next_day=True, sleep blocks, and evening routines
        (which can cross midnight) are handled specially.
    """
    if not items:
        return
    
    items_to_check = []
    for item in items:
        if item.get("next_day") or item.get("type") == "sleep":
            continue
        
        if item.get("type") == "fixed_event":
            name = item.get("name", "").lower()
            event_id = item.get("event_id", "").lower()
            start_time = item.get("start_time", "00:00")
            
            if ("evening" in name or "evening" in event_id) and "routine" in (name + event_id):
                start_minutes = _time_to_minutes(start_time)
                if start_minutes < 120:
                    continue
        
        items_to_check.append(item)
    
    if not items_to_check:
        return
    
    for i in range(len(items_to_check) - 1):
        current_start = _time_to_minutes(items_to_check[i].get("start_time", "00:00"))
        next_start = _time_to_minutes(items_to_check[i + 1].get("start_time", "00:00"))
        
        if current_start > next_start:
            errors["ordering"].append(
                f"Items not in chronological order: "
                f"'{items_to_check[i].get('name')}' ({items_to_check[i].get('start_time')}) "
                f"after '{items_to_check[i + 1].get('name')}' ({items_to_check[i + 1].get('start_time')})"
            )


def _time_to_minutes(time_str: str) -> int:
    """
    Converts HH:MM time string to minutes since midnight.
    
    Educational Note:
        Minute-based representation simplifies time arithmetic
        and comparison operations.
    """
    if time_str in ["24:00"]:
        return 1440
    
    try:
        parts = time_str.split(":")
        hours = int(parts[0])
        minutes = int(parts[1])
        return hours * 60 + minutes
    except (ValueError, AttributeError, IndexError):
        raise ValueError(f"Invalid time format: {time_str}")
