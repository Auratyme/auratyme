"""
Solver Data Models for Constraint-Based Scheduling.

Defines input/output structures for the constraint satisfaction programming (CSP)
solver. These immutable dataclasses ensure deterministic behavior and prevent
accidental modifications during solver execution.

Educational Context:
    Frozen dataclasses enforce immutability, a critical property in constraint
    programming where solver state must remain consistent. This prevents subtle
    bugs from state mutation during optimization and makes debugging easier
    since inputs cannot change mid-execution.
"""

import logging
from dataclasses import dataclass, field
from datetime import date, time
from typing import Dict, List, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FixedEventInterval:
    """
    Represents an immovable time block in the schedule.

    Fixed events are hard constraints that cannot be moved, shortened, or
    removed by the solver. They represent appointments, meetings, or other
    commitments that must be respected.

    Args:
        id: Unique identifier for this fixed event
        start_minutes: Start time in minutes since midnight (0-1439)
        end_minutes: End time in minutes since midnight (1-1440)
        name: Optional human-readable name for the event

    Educational Note:
        Using minute-based representation (0-1440) simplifies constraint
        programming compared to datetime objects which have timezone and
        DST complications. The solver operates in a single-day context.
    """
    id: str
    start_minutes: int
    end_minutes: int
    name: Optional[str] = None

    def __post_init__(self):
        """
        Validates fixed event constraints.

        Educational Note:
            Validation in __post_init__ catches data errors early, before
            the solver runs. This fail-fast approach prevents wasted
            computation on invalid inputs.
        """
        self._validate_time_bounds()
        self._validate_duration()

    def _validate_time_bounds(self) -> None:
        """
        Ensures time values are within a single day range.
        """
        if not (0 <= self.start_minutes <= 1439 and 0 <= self.end_minutes <= 1440):
            raise ValueError(f"Event {self.id} time out of range [0-1440]")

    def _validate_duration(self) -> None:
        """
        Ensures event has positive duration.
        """
        if self.end_minutes <= self.start_minutes:
            raise ValueError(f"Event {self.id} end must be after start")


@dataclass(frozen=True)
class SolverTask:
    """
    Task representation optimized for constraint solver.

    This structure contains only the information needed by the CP-SAT solver,
    stripping away presentation details to focus on scheduling constraints.

    Args:
        id: Unique task identifier
        duration_minutes: How long the task takes (must be positive)
        priority: Relative importance (higher = more important)
        energy_level: Required energy level (1=low, 2=medium, 3=high)
        earliest_start_minutes: Cannot start before this time
        latest_end_minutes: Must finish by this time
        dependencies: List of task IDs that must complete first

    Educational Note:
        Separating solver-specific data from domain models follows the
        Single Responsibility Principle. The solver doesn't need to know
        about task descriptions, tags, or UI metadata.
    """
    id: UUID
    duration_minutes: int
    priority: int = 3
    energy_level: int = 2
    earliest_start_minutes: Optional[int] = None
    latest_end_minutes: Optional[int] = None
    dependencies: List[UUID] = field(default_factory=list)

    def __post_init__(self):
        """
        Validates task is schedulable.
        """
        self._validate_duration()
        self._validate_time_window()

    def _validate_duration(self) -> None:
        """
        Ensures task has positive duration.
        """
        if self.duration_minutes <= 0:
            raise ValueError(f"Task {self.id} duration must be positive")

    def _validate_time_window(self) -> None:
        """
        Validates time constraints are feasible.
        """
        if self._has_time_constraints() and self._is_time_window_impossible():
            raise ValueError(f"Task {self.id} has impossible time constraints")

    def _has_time_constraints(self) -> bool:
        """
        Checks if task has explicit time boundaries.
        """
        return self.earliest_start_minutes is not None and self.latest_end_minutes is not None

    def _is_time_window_impossible(self) -> bool:
        """
        Determines if time window is too small for task duration.
        """
        window_size = self.latest_end_minutes - self.earliest_start_minutes
        return window_size < self.duration_minutes


@dataclass(frozen=True)
class SolverInput:
    """
    Complete input bundle for constraint solver execution.

    Packages all data needed for scheduling in a single immutable structure,
    following the principle that solver should be a pure function.

    Args:
        target_date: The date being scheduled
        tasks: List of tasks to schedule
        fixed_events: Immovable time blocks
        day_start_minutes: When the scheduling day begins
        day_end_minutes: When the scheduling day ends
        user_energy_pattern: Hourly energy levels (hour -> energy 0.0-1.0)

    Educational Note:
        Immutable input structures make the solver deterministic (same input
        always produces same output) and thread-safe. This is crucial for
        testing and parallel execution.
    """
    target_date: date
    tasks: List[SolverTask]
    fixed_events: List[FixedEventInterval]
    day_start_minutes: int = 0
    day_end_minutes: int = 1440
    user_energy_pattern: Dict[int, float] = field(default_factory=dict)

    def __post_init__(self):
        """
        Validates solver input constraints.
        """
        self._validate_day_bounds()
        self._validate_energy_pattern()

    def _validate_day_bounds(self) -> None:
        """
        Ensures day boundaries are valid.
        """
        if not (0 <= self.day_start_minutes < self.day_end_minutes <= 1440):
            raise ValueError("Invalid day boundaries")

    def _validate_energy_pattern(self) -> None:
        """
        Checks energy pattern has valid hour keys.
        """
        for hour in self.user_energy_pattern:
            if not (0 <= hour <= 23):
                raise ValueError(f"Invalid hour {hour} in energy pattern")


@dataclass(frozen=True)
class ScheduledTaskInfo:
    """
    Solver output representing a scheduled task.

    Args:
        task_id: Reference to the original task
        start_time: When the task is scheduled to begin
        end_time: When the task is scheduled to end
        task_date: The date of this scheduled task

    Educational Note:
        Separating input (SolverTask) from output (ScheduledTaskInfo) follows
        CQRS (Command Query Responsibility Segregation) pattern. This clear
        separation prevents confusion about what data flows which direction.
    """
    task_id: UUID
    start_time: time
    end_time: time
    task_date: date
