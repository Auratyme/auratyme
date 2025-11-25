"""
Task package for task management and prioritization.

Exports core task structures and prioritization logic.

Educational Context:
    Clean package structure with focused modules:
    - models: Data structures
    - urgency: Deadline calculations  
    - prioritizer: Scoring logic
    - energy_matcher: Energy-based scheduling
    - scheduling: Simple heuristics
"""

from .models import EnergyLevel, Task, TaskPriority
from .prioritizer import TaskPrioritizer
from .urgency import calculate_time_urgency_factor
from .energy_matcher import find_best_energy_match_time
from .scheduling import recommend_task_order

__all__ = [
    "EnergyLevel",
    "Task",
    "TaskPriority",
    "TaskPrioritizer",
    "calculate_time_urgency_factor",
    "find_best_energy_match_time",
    "recommend_task_order",
]
