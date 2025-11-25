"""
Schedule metrics calculation.

This module computes quality and balance metrics for generated schedules,
providing insights into time allocation across different activity types.
"""

import logging
from typing import Any, Dict, List, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.task import Task

logger = logging.getLogger(__name__)


def calculate_schedule_metrics(
    items: List[Dict[str, Any]],
    tasks: List["Task"]
) -> Dict[str, Any]:
    """
    Calculates metrics for the completed schedule.
    
    Educational Note:
        Metrics provide transparency into schedule composition,
        helping users understand time allocation and identify
        potential imbalances between work, rest, and personal time.
    """
    try:
        time_allocations = _calculate_time_by_type(items)
        completion_stats = _calculate_completion_stats(items, tasks)
        balance_metrics = _calculate_balance_metrics(time_allocations)
        
        metrics = {
            **time_allocations,
            **completion_stats,
            **balance_metrics
        }
        
        logger.info(f"Calculated metrics: {metrics}")
        return metrics
    except Exception:
        logger.exception("Error calculating metrics.")
        return {"status": "error"}


def _calculate_time_by_type(
    items: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Calculates total minutes spent on each activity type.
    
    Educational Note:
        Separates different time categories to understand
        how schedule balances productivity, rest, and personal needs.
    """
    return {
        "total_task_minutes": _sum_task_time(items),
        "total_break_minutes": _sum_break_time(items),
        "total_fixed_minutes": _sum_fixed_event_time(items),
        "total_sleep_minutes": _sum_sleep_time(items),
        "total_meal_minutes": _sum_meal_time(items),
        "total_routine_minutes": _sum_routine_time(items),
        "total_activity_minutes": _sum_activity_time(items),
    }


def _sum_task_time(items: List[Dict[str, Any]]) -> int:
    """
    Sums duration of all task items.
    
    Educational Note:
        Task time represents productive work blocks scheduled
        from user's task list.
    """
    return sum(
        item.get("duration_minutes", 0)
        for item in items
        if item.get("type") == "task"
    )


def _sum_break_time(items: List[Dict[str, Any]]) -> int:
    """
    Sums duration of all break and relaxation items.
    
    Educational Note:
        Includes various break types (quick, short, relaxation, free time)
        to ensure adequate rest periods throughout day.
    """
    break_types = {"break", "quick_break", "short_break", "relaxation", "free_time"}
    
    return sum(
        item.get("duration_minutes", 0)
        for item in items
        if item.get("type") in break_types
    )


def _sum_fixed_event_time(items: List[Dict[str, Any]]) -> int:
    """
    Sums duration of all fixed events.
    
    Educational Note:
        Fixed events (meetings, appointments) are non-negotiable
        time blocks that constrain schedule flexibility.
    """
    return sum(
        item.get("duration_minutes", 0)
        for item in items
        if item.get("type") == "fixed_event"
    )


def _sum_sleep_time(items: List[Dict[str, Any]]) -> int:
    """
    Sums duration of sleep periods.
    
    Educational Note:
        Sleep tracked separately from other fixed events
        due to its critical importance for health and performance.
        After merge_sleep_blocks(), type changes to "sleep".
    """
    return sum(
        item.get("duration_minutes", 0)
        for item in items
        if (item.get("type") == "sleep" or 
            (item.get("type") == "fixed_event" and "sleep" in item.get("event_id", "")))
    )


def _sum_meal_time(items: List[Dict[str, Any]]) -> int:
    """
    Sums duration of all meal items.
    
    Educational Note:
        Meal timing affects energy levels and digestive health.
        Tracked separately for nutrition-conscious scheduling.
    """
    return sum(
        item.get("duration_minutes", 0)
        for item in items
        if item.get("type") == "meal"
    )


def _sum_routine_time(items: List[Dict[str, Any]]) -> int:
    """
    Sums duration of routine items (morning/evening rituals).
    
    Educational Note:
        Routines provide structure and consistency,
        important for habit formation and daily rhythm.
    """
    return sum(
        item.get("duration_minutes", 0)
        for item in items
        if item.get("type") == "routine"
    )


def _sum_activity_time(items: List[Dict[str, Any]]) -> int:
    """
    Sums duration of physical activity items.
    
    Educational Note:
        Physical activity crucial for health, cognitive function,
        and stress management. Tracked for wellness balance.
    """
    return sum(
        item.get("duration_minutes", 0)
        for item in items
        if item.get("type") == "activity"
    )


def _calculate_completion_stats(
    items: List[Dict[str, Any]],
    tasks: List["Task"]
) -> Dict[str, Any]:
    """
    Calculates task scheduling completion statistics.
    
    Educational Note:
        Completion percentage indicates scheduling success rate.
        Unscheduled tasks may indicate over-commitment or constraint conflicts.
    """
    scheduled_ids = _get_scheduled_task_ids(items)
    original_ids = _get_original_task_ids(tasks)
    unscheduled_count = len(original_ids - scheduled_ids)
    
    completion_pct = _calculate_completion_percentage(
        scheduled_ids, original_ids
    )
    
    return {
        "unscheduled_tasks": unscheduled_count,
        "task_completion_pct": completion_pct
    }


def _get_scheduled_task_ids(
    items: List[Dict[str, Any]]
) -> Set[str]:
    """
    Extracts IDs of tasks that were scheduled.
    
    Educational Note:
        Set data structure enables efficient comparison
        with original task list to find unscheduled items.
    """
    return {
        item.get("task_id")
        for item in items
        if item.get("type") == "task"
    }


def _get_original_task_ids(
    tasks: List["Task"]
) -> Set[str]:
    """
    Extracts IDs of all incomplete tasks.
    
    Educational Note:
        Filters out completed tasks since they don't need
        scheduling. Converts UUIDs to strings for comparison.
    """
    return {
        str(task.id)
        for task in tasks
        if not task.completed
    }


def _calculate_completion_percentage(
    scheduled_ids: Set[str],
    original_ids: Set[str]
) -> float:
    """
    Calculates percentage of tasks successfully scheduled.
    
    Educational Note:
        100% when all tasks scheduled or no tasks provided.
        Lower percentage indicates scheduling challenges.
    """
    if not original_ids:
        return 100.0
    
    return len(scheduled_ids) / len(original_ids) * 100


def _calculate_balance_metrics(
    time_allocations: Dict[str, int]
) -> Dict[str, Any]:
    """
    Calculates work-life balance and time category aggregations.
    
    Educational Note:
        Aggregates individual categories into broader metrics
        (productive, personal, rest) for holistic schedule assessment.
    """
    total_productive = _calculate_productive_time(time_allocations)
    total_personal = _calculate_personal_time(time_allocations)
    total_rest = _calculate_rest_time(time_allocations)
    
    work_life_ratio = _calculate_work_life_ratio(
        total_personal, total_productive
    )
    
    return {
        "total_productive_minutes": total_productive,
        "total_personal_minutes": total_personal,
        "total_rest_minutes": total_rest,
        "work_life_balance": work_life_ratio
    }


def _calculate_productive_time(
    time_allocations: Dict[str, int]
) -> int:
    """
    Sums task and activity time as productive time.
    
    Educational Note:
        Productive time includes both work tasks and
        health-promoting physical activities.
    """
    return (
        time_allocations["total_task_minutes"] +
        time_allocations["total_activity_minutes"]
    )


def _calculate_personal_time(
    time_allocations: Dict[str, int]
) -> int:
    """
    Sums meal and routine time as personal time.
    
    Educational Note:
        Personal time represents self-care activities
        essential for wellbeing and sustainability.
    """
    return (
        time_allocations["total_meal_minutes"] +
        time_allocations["total_routine_minutes"]
    )


def _calculate_rest_time(
    time_allocations: Dict[str, int]
) -> int:
    """
    Sums break and sleep time as rest time.
    
    Educational Note:
        Rest time critical for recovery, preventing burnout,
        and maintaining long-term productivity.
    """
    return (
        time_allocations["total_break_minutes"] +
        time_allocations["total_sleep_minutes"]
    )


def _calculate_work_life_ratio(
    personal_time: int,
    productive_time: int
) -> float:
    """
    Calculates ratio of personal to productive time.
    
    Educational Note:
        Higher ratio indicates more balanced schedule.
        Division by max(1, productive) prevents divide-by-zero.
    """
    denominator = max(1, productive_time)
    ratio = personal_time / denominator * 100
    
    return round(ratio, 1)
