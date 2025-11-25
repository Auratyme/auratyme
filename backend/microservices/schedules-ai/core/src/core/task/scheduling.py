"""
Task scheduling utilities and helpers.

Provides simple heuristic scheduling functions for task ordering
without full constraint solving.

Educational Context:
    These are lightweight alternatives to full constraint solver.
    Useful for quick estimates or when solver would be overkill.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from .models import Task
from .prioritizer import TaskPrioritizer

logger = logging.getLogger(__name__)


def normalize_time_window(
    start: datetime,
    end: datetime
) -> Tuple[datetime, datetime]:
    """
    Ensures time window is timezone-aware.
    """
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    return start, end


def get_task_placement_time(
    task: Task,
    current_time: datetime,
    window_start: datetime
) -> datetime:
    """
    Determines when to place task respecting its earliest start.
    """
    task_earliest = task.earliest_start or window_start
    
    if task_earliest.tzinfo is None:
        task_earliest = task_earliest.replace(tzinfo=timezone.utc)
    
    return max(current_time, task_earliest)


def task_fits_in_window(
    placement_time: datetime,
    task: Task,
    window_end: datetime
) -> bool:
    """
    Checks if task can complete before window ends.
    """
    return placement_time + task.duration <= window_end


def recommend_task_order(
    tasks: List[Task],
    start_datetime: datetime,
    end_datetime: datetime,
    prioritizer: TaskPrioritizer
) -> List[Tuple[Task, datetime]]:
    """
    Creates heuristic schedule by placing tasks in priority order.
    
    Args:
        tasks: Tasks to schedule
        start_datetime: Window start
        end_datetime: Window end
        prioritizer: TaskPrioritizer for sorting
    
    Returns:
        List of (task, start_time) tuples
    
    Educational Note:
        Simple greedy algorithm: sort by priority, place tasks sequentially.
        Fast but doesn't handle constraints like dependencies or energy matching.
        For full scheduling, use ConstraintSchedulerSolver instead.
    """
    logger.warning("recommend_task_order is heuristic - use ConstraintSchedulerSolver for proper scheduling")
    
    if not tasks:
        return []
    
    start_datetime, end_datetime = normalize_time_window(start_datetime, end_datetime)
    prioritized = prioritizer.prioritize(tasks, start_datetime)
    
    schedule = []
    current_time = start_datetime
    
    for task in prioritized:
        placement_time = get_task_placement_time(task, current_time, start_datetime)
        
        if task_fits_in_window(placement_time, task, end_datetime):
            schedule.append((task, placement_time))
            current_time = placement_time + task.duration
        else:
            logger.debug(f"Task '{task.title}' doesn't fit in window")
        
        if current_time >= end_datetime:
            break
    
    return schedule
