"""
Task urgency calculation based on deadline proximity.

Calculates how urgent a task is based on time remaining until deadline.
Uses exponential curve to increase urgency as deadline approaches.

Educational Context:
    Urgency calculation prevents procrastination by increasing task priority
    as deadlines approach. Exponential curve (time_elapsed^2) creates
    accelerating urgency rather than linear.
"""

import logging
import math
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def normalize_datetime_to_utc(dt: datetime) -> datetime:
    """
    Ensures datetime is timezone-aware (UTC).
    
    Educational Note:
        Defensive programming - always work with UTC to avoid timezone bugs.
    """
    if dt.tzinfo is None:
        logger.warning("Naive datetime converted to UTC")
        return dt.replace(tzinfo=timezone.utc)
    return dt


def is_deadline_passed(deadline: datetime, current_time: datetime) -> bool:
    """
    Checks if deadline has already passed.
    """
    return deadline <= current_time


def calculate_total_lead_time(deadline: datetime, created_at: datetime) -> float:
    """
    Calculates total time from task creation to deadline.
    
    Returns:
        Lead time in seconds
    """
    return (deadline - created_at).total_seconds()


def calculate_time_elapsed(current_time: datetime, created_at: datetime) -> float:
    """
    Calculates time since task was created.
    
    Returns:
        Elapsed time in seconds
    """
    return (current_time - created_at).total_seconds()


def calculate_elapsed_ratio(elapsed: float, total: float) -> float:
    """
    Calculates what fraction of total time has elapsed.
    
    Educational Note:
        Ratio (0.0-1.0) represents progress toward deadline.
        0.0 = just created, 1.0 = deadline reached.
    """
    if total <= 0:
        return 1.0
    return max(0.0, elapsed / total)


def apply_exponential_urgency_curve(elapsed_ratio: float) -> float:
    """
    Applies exponential curve to elapsed ratio.
    
    Educational Note:
        Squaring creates accelerating urgency:
        - 0.5 elapsed → 0.25 urgency (still relaxed)
        - 0.7 elapsed → 0.49 urgency (getting urgent)
        - 0.9 elapsed → 0.81 urgency (very urgent)
    """
    return math.pow(elapsed_ratio, 2)


def clamp_urgency(urgency: float) -> float:
    """
    Ensures urgency stays in valid range 0.0-1.0.
    """
    return min(1.0, max(0.0, urgency))


def calculate_time_urgency_factor(
    task,
    current_datetime: datetime = None
) -> float:
    """
    Calculates urgency factor (0.0-1.0) based on deadline proximity.
    
    Returns:
        0.0 = no deadline or just created
        1.0 = deadline passed or imminent
    
    Educational Note:
        Exponential curve means urgency stays low early, then
        rapidly increases as deadline approaches. This matches
        human perception of urgency.
    """
    if not task.deadline:
        return 0.0
    
    now = current_datetime or datetime.now(timezone.utc)
    now = normalize_datetime_to_utc(now)
    deadline = normalize_datetime_to_utc(task.deadline)
    
    if is_deadline_passed(deadline, now):
        return 1.0
    
    total_lead = calculate_total_lead_time(deadline, task.created_at)
    
    if total_lead <= 0:
        return 1.0
    
    elapsed = calculate_time_elapsed(now, task.created_at)
    ratio = calculate_elapsed_ratio(elapsed, total_lead)
    urgency = apply_exponential_urgency_curve(ratio)
    
    return clamp_urgency(urgency)
