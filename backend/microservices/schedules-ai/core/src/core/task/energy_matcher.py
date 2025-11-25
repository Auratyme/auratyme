"""
Energy pattern matching for task scheduling.

Matches task energy requirements to user's hourly energy levels
to find optimal scheduling times.

Educational Context:
    Energy matching improves productivity by scheduling high-energy
    tasks during high-energy periods. Simple heuristic search finds
    best time slots within constraints.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict

from .models import EnergyLevel, Task

logger = logging.getLogger(__name__)


def normalize_task_energy(task: Task) -> float:
    """
    Converts task energy level to 0.0-1.0 scale.
    
    Educational Note:
        Normalization makes task energy comparable to user energy pattern.
    """
    max_energy = max(e.value for e in EnergyLevel)
    return task.energy_level.value / max_energy


def get_hour_from_datetime(dt: datetime) -> int:
    """
    Extracts hour (0-23) from datetime.
    """
    return dt.hour


def calculate_energy_match(user_energy: float, task_energy: float) -> float:
    """
    Calculates how well user and task energy levels match.
    
    Returns:
        Score 0.0-1.0 where 1.0 is perfect match
    
    Educational Note:
        Using absolute difference: perfect match when energies equal,
        poor match when they differ significantly.
    """
    return 1.0 - abs(user_energy - task_energy)


def can_fit_task(
    check_time: datetime,
    task: Task,
    latest_end: datetime
) -> bool:
    """
    Checks if task can complete before deadline.
    """
    return check_time + task.duration <= latest_end


def find_best_energy_match_time(
    task: Task,
    earliest_start: datetime,
    latest_end: datetime,
    energy_pattern: Dict[int, float],
    step: timedelta = timedelta(minutes=15),
    lookahead: timedelta = timedelta(hours=1)
) -> datetime:
    """
    Finds optimal time to schedule task based on energy matching.
    
    Args:
        task: Task to schedule
        earliest_start: Cannot start before this
        latest_end: Must finish before this
        energy_pattern: User's hourly energy levels
        step: Time increment for search
        lookahead: Maximum search duration
    
    Returns:
        Best start time within constraints
    
    Educational Note:
        Greedy search: checks each time slot, keeps track of best match.
        Not guaranteed optimal but fast and good enough for heuristics.
    """
    best_time = earliest_start
    best_score = -1.0
    task_energy = normalize_task_energy(task)
    
    search_end = calculate_search_end(earliest_start, latest_end, lookahead, task)
    current_time = earliest_start
    
    while current_time <= search_end:
        if can_fit_task(current_time, task, latest_end):
            score = calculate_energy_score(current_time, task_energy, energy_pattern)
            
            if score > best_score:
                best_score = score
                best_time = current_time
        
        current_time += step
    
    return best_time


def calculate_search_end(
    earliest_start: datetime,
    latest_end: datetime,
    lookahead: timedelta,
    task: Task
) -> datetime:
    """
    Determines where to stop searching for time slots.
    
    Educational Note:
        Search end is minimum of: earliest + lookahead, or latest time
        where task can still complete. This prevents searching impossibly
        late slots.
    """
    lookahead_end = earliest_start + lookahead
    completion_deadline = latest_end - task.duration
    return min(lookahead_end, completion_deadline)


def calculate_energy_score(
    check_time: datetime,
    task_energy: float,
    energy_pattern: Dict[int, float]
) -> float:
    """
    Calculates energy match score for a specific time.
    """
    hour = get_hour_from_datetime(check_time)
    user_energy = energy_pattern.get(hour, 0.5)
    return calculate_energy_match(user_energy, task_energy)
